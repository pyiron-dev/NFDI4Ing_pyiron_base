import os
import subprocess


def generate_mesh(gmsh_input_file: str, domain_size: float = 2.0) -> str:
    stage_name = "preprocessing"
    gmsh_output_file = os.path.join(stage_name, "square.msh")
    os.makedirs(stage_name, exist_ok=True)
    _ = subprocess.check_output(
        [
            "conda", "run", "-n", stage_name, "gmsh", "-2", "-setnumber",
            "domain_size", str(domain_size), gmsh_input_file, "-o", gmsh_output_file
        ],
        universal_newlines=True,
    ).split("\n")
    return gmsh_output_file


def convert_to_xdmf(gmsh_output_file : str) -> str:
    stage_name = "preprocessing"
    meshio_output = os.path.join(stage_name, "quare.xdmf")
    os.makedirs(stage_name, exist_ok=True)
    _ = subprocess.check_output(
        ["conda", "run", "-n", stage_name, "meshio", "convert", gmsh_output_file, meshio_output],
        universal_newlines=True,
    ).split("\n")
    return meshio_output


def poisson(meshio_output: str) -> dict:
    stage_name = "processing"
    os.makedirs(stage_name, exist_ok=True)
    poisson_output_pvd_file = os.path.join(stage_name, "poisson.pvd")
    poisson_output_numdofs_file = os.path.join(stage_name, "numdofs.txt",)
    subprocess.check_output(
        [
            "conda", "run", "-n", stage_name, "python", "source/poisson.py",
            "--mesh", meshio_output, "--degree", "2",
            "--outputfile", poisson_output_pvd_file, "--num-dofs", poisson_output_numdofs_file
        ],
        universal_newlines=True,
    ).split("\n")
    return {
        "numdofs": _poisson_collect_output(numdofs_file=poisson_output_numdofs_file),
        "poisson_output_pvd_file": poisson_output_pvd_file,
    }


def plot_over_line(poisson_output_pvd_file: str) -> str:
    stage_name = "postprocessing"
    pvbatch_output_file = os.path.join(stage_name, "plotoverline.csv")
    os.makedirs(stage_name, exist_ok=True)
    subprocess.check_output(
        ["conda", "run", "-n", stage_name, "pvbatch", "source/postprocessing.py", poisson_output_pvd_file, pvbatch_output_file],
        universal_newlines=True,
    ).split("\n")
    return pvbatch_output_file


def substitute_macros(macros_source: str, pvbatch_output_file: str, ndofs: int, domain_size: float = 2.0) -> str:
    stage_name = "postprocessing"
    macros_output_file = "macros.tex"
    os.makedirs(stage_name, exist_ok=True)
    subprocess.check_output(
        [
            "conda", "run", "-n", stage_name, "python", "source/prepare_paper_macros.py",
            "--macro-template-file", macros_source, "--plot-data-path", pvbatch_output_file,
            "--domain-size", str(domain_size), "--num-dofs", str(ndofs),
            "--output-macro-file", macros_output_file,
        ],
        universal_newlines=True,
    ).split("\n")
    return macros_output_file


def compile_paper(paper_source: str) -> str:
    stage_name = "postprocessing"
    paper_output = "paper.tex"
    os.makedirs(stage_name, exist_ok=True)
    subprocess.check_output(
        ["cp", paper_source, paper_output],
        universal_newlines=True,
    ).split("\n")
    subprocess.check_output(
        ["conda", "run", "-n", stage_name, "tectonic", paper_output],
        universal_newlines=True,
    ).split("\n")
    return paper_output


def _poisson_collect_output(numdofs_file: str) -> int:
    with open(os.path.join(numdofs_file), "r") as f:
        return int(f.read())
