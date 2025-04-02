import os
import subprocess
import shutil

source_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "source")


def generate_mesh(gmsh_input_file: str, domain_size: float = 2.0) -> str:
    stage_name = "preprocessing"
    gmsh_output_file_name = "square.msh"
    gmsh_output_file = os.path.join(stage_name, gmsh_output_file_name)
    gmsh_input_file_name = os.path.basename(gmsh_input_file)
    os.makedirs(stage_name, exist_ok=True)
    shutil.copyfile(gmsh_input_file, os.path.join(os.path.abspath(stage_name), gmsh_input_file_name))
    output = subprocess.check_output(
        [
            "conda", "run", "-n", stage_name, "gmsh", "-2", "-setnumber",
            "domain_size", str(domain_size), gmsh_input_file_name, "-o", gmsh_output_file_name
        ],
        cwd=stage_name,
        universal_newlines=True,
    ).split("\n")
    # print(output)
    return os.path.abspath(gmsh_output_file)


def convert_to_xdmf(gmsh_output_file : str) -> str:
    stage_name = "preprocessing"
    meshio_output_file_name = "square.xdmf"
    meshio_output_file = os.path.join(stage_name, meshio_output_file_name)
    gmsh_output_file_name = os.path.basename(gmsh_output_file)
    os.makedirs(stage_name, exist_ok=True)
    gmsh_input_file = os.path.join(os.path.abspath(stage_name), gmsh_output_file_name)
    if gmsh_input_file != gmsh_output_file:
        shutil.copyfile(gmsh_output_file_name, gmsh_input_file)
    output = subprocess.check_output(
        ["conda", "run", "-n", stage_name, "meshio", "convert", gmsh_output_file_name, meshio_output_file_name],
        cwd=stage_name,
        universal_newlines=True,
    ).split("\n")
    # print(output)
    return {
        "xdmf": os.path.abspath(meshio_output_file),
        "h5": os.path.join(os.path.abspath(stage_name), "square.h5"),
    }


def poisson(meshio_output_xdmf: str, meshio_output_h5: str) -> dict:
    stage_name = "processing"
    os.makedirs(stage_name, exist_ok=True)
    poisson_output_pvd_file_name = "poisson.pvd"
    poisson_output_pvd_file = os.path.join(stage_name, poisson_output_pvd_file_name)
    poisson_output_numdofs_file_name = "numdofs.txt"
    source_file_name = "poisson.py"
    source_file = os.path.join(source_directory, source_file_name)
    shutil.copyfile(source_file, os.path.join(stage_name, source_file_name))
    shutil.copyfile(meshio_output_xdmf, os.path.join(stage_name, os.path.basename(meshio_output_xdmf)))
    shutil.copyfile(meshio_output_h5, os.path.join(stage_name, os.path.basename(meshio_output_h5)))
    output = subprocess.check_output(
        [
            "conda", "run", "-n", stage_name, "python", "poisson.py",
            "--mesh", os.path.basename(meshio_output_xdmf), "--degree", "2",
            "--outputfile", poisson_output_pvd_file_name, "--num-dofs", poisson_output_numdofs_file_name
        ],
        cwd=stage_name,
        universal_newlines=True,
    ).split("\n")
    # print(output)
    return {
        "numdofs": _poisson_collect_output(numdofs_file=os.path.join(stage_name, poisson_output_numdofs_file_name)),
        "poisson_output_pvd_file": os.path.abspath(poisson_output_pvd_file),
        "poisson_output_vtu_file": os.path.abspath(os.path.join(stage_name, "poisson000000.vtu")),
    }


def plot_over_line(poisson_output_pvd_file: str, poisson_output_vtu_file: str) -> str:
    stage_name = "postprocessing"
    pvbatch_output_file_name = "plotoverline.csv"
    os.makedirs(stage_name, exist_ok=True)
    source_file_name = "postprocessing.py"
    source_file = os.path.join(source_directory, source_file_name)
    shutil.copyfile(source_file, os.path.join(stage_name, source_file_name))
    shutil.copyfile(poisson_output_pvd_file, os.path.join(stage_name, os.path.basename(poisson_output_pvd_file)))
    shutil.copyfile(poisson_output_vtu_file, os.path.join(stage_name, os.path.basename(poisson_output_vtu_file)))
    output = subprocess.check_output(
        ["conda", "run", "-n", stage_name, "pvbatch", "postprocessing.py", os.path.basename(poisson_output_pvd_file), pvbatch_output_file_name],
        cwd=stage_name,
        universal_newlines=True,
    ).split("\n")
    # print(output)
    return os.path.abspath(os.path.join("postprocessing", pvbatch_output_file_name))


def substitute_macros(pvbatch_output_file: str, ndofs: int, domain_size: float = 2.0) -> str:
    stage_name = "postprocessing"
    macros_output_file_name = "macros.tex"
    os.makedirs(stage_name, exist_ok=True)
    source_file_name = "prepare_paper_macros.py"
    source_file = os.path.join(source_directory, source_file_name)
    shutil.copyfile(source_file, os.path.join(stage_name, source_file_name))
    template_file_name = "macros.tex.template"
    template_file = os.path.join(source_directory, template_file_name)
    shutil.copyfile(template_file, os.path.join(stage_name, template_file_name))
    pvbatch_input_file = os.path.join(stage_name, os.path.basename(pvbatch_output_file))
    if os.path.abspath(pvbatch_input_file) != pvbatch_output_file:
        shutil.copyfile(pvbatch_output_file, pvbatch_input_file)
    output = subprocess.check_output(
        [
            "conda", "run", "-n", stage_name, "python", "prepare_paper_macros.py",
            "--macro-template-file", template_file_name, "--plot-data-path", os.path.basename(pvbatch_output_file),
            "--domain-size", str(domain_size), "--num-dofs", str(ndofs),
            "--output-macro-file", macros_output_file_name,
        ],
        cwd=stage_name,
        universal_newlines=True,
    ).split("\n")
    # print(output)
    return os.path.abspath(os.path.join(stage_name, macros_output_file_name))


def compile_paper(macros_tex: str, plot_file: str) -> str:
    stage_name = "postprocessing"
    paper_output = "paper.pdf"
    os.makedirs(stage_name, exist_ok=True)
    source_file_name = "paper.tex"
    source_file = os.path.join(source_directory, source_file_name)
    shutil.copyfile(source_file, os.path.join(stage_name, source_file_name))
    plot_input_file = os.path.join(stage_name, os.path.basename(plot_file))
    if os.path.abspath(plot_input_file) != plot_file:
        shutil.copyfile(plot_file, plot_input_file)
    macros_input_file = os.path.join(stage_name, os.path.basename(macros_tex))
    if os.path.abspath(macros_input_file) != macros_tex:
        shutil.copyfile(macros_tex, macros_input_file)
    output = subprocess.check_output(
        ["conda", "run", "-n", stage_name, "tectonic", source_file_name],
        universal_newlines=True,
        cwd=stage_name,
    ).split("\n")
    # print(output)
    return os.path.abspath(os.path.join(stage_name, paper_output))


def _poisson_collect_output(numdofs_file: str) -> int:
    with open(os.path.join(numdofs_file), "r") as f:
        return int(f.read())
