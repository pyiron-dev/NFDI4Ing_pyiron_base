# NFDI4Ing pyiron_base
This example implements the workflow defined by NFDI4Ing in pyiron_base. More details about the workflow are available in their [repository](https://github.com/BAMresearch/NFDI4IngScientificWorkflowRequirements) and the corresponding [publication](https://preprints.inggrid.org/repository/view/5/).

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/pyiron-dev/NFDI4Ing_pyiron_base/HEAD?labpath=example.ipynb)

Content of this repository: 

* `source/envs` - separate conda environments for `preprocessing`, `processing` and `postprocessing` - copied from [BAMresearch/NFDI4IngScientificWorkflowRequirements](https://github.com/BAMresearch/NFDI4IngScientificWorkflowRequirements/tree/main/exemplary_workflow/source)
* `source` - python scripts and template files for the workflow - copied from [BAMresearch/NFDI4IngScientificWorkflowRequirements](https://github.com/BAMresearch/NFDI4IngScientificWorkflowRequirements/tree/main/exemplary_workflow/source)
* `apt.txt` - `libGL` and `libeGL` have to be installed via `apt`.
* `basic.ipynb` - Jupyter notebook using python subprocesses to executed the individual tasks based on the explanation in [BAMresearch/NFDI4IngScientificWorkflowRequirements](https://github.com/BAMresearch/NFDI4IngScientificWorkflowRequirements/blob/main/docs/exemplarywf.rst)
* `basic_variables.ipynb` - similar to `basic.ipynb` just using variables to define file names only once. 
* `environment.yml` - conda environment with `pyiron_base` to execute the workflow.
* `example.ipynb` - workflow implemented in `pyiron_base` using the `create_job_class()` function.
* `postBuild` - currently this example is based on a pre-release version of `pyiron_base` which is installed using the `postBuild` script. 
