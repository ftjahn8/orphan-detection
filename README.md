![Linting](https://img.shields.io/github/workflow/status/ftjahn8/orphan-detection/Linting?label=Linting)
![Language](https://img.shields.io/github/languages/top/ftjahn8/orphan-detection)
![Version](https://img.shields.io/badge/python--version-3.10-blue)
![Docker](https://img.shields.io/badge/Docker-yes-brightgreen)


# Orphan Detection
Orphan-Detection-Python v.1.0.0  
25.06.2022 - Felix Etzkorn

## Acknowledgement

This work is heavily based on the work of Stijn Pletinckx, Kevin Borgolte & Tobais Fiebig in their paper 
["Out of Sight, Out of Mind: Detecting Orphaned Web Pages at Internet-Scale"](https://kevin.borgolte.me/files/pdf/ccs2021-out-of-sight-out-of-mind.pdf) and their original implementation available [here](https://github.com/OrphanDetection/orphan-detection).


## Major Changes (compared to the original Implementation)  
- no Bash, just Python  
  => easier to read, easier to execute (on Windows / without Docker)  
- restructure of all scripts in separate modules  
- introduction of new cli arguments, removed parameter files  
  => `Data`-directory only for output & result-files  
  => can now be moved from rest of code / easier to export from docker container  
- removed unnecessary python modules, implemented short functions myself  
  => reduced dependencies on other modules and their development  
  => less risk to fail the docker build due to incompatible versions  

- improvements on orphan detection part
  - corrected date filter (step after download) for detection of possible orphans
  - improved ressource filter
  - reworked `DUDE`-step completely
    => now better results (especially for domains with a lot of subdomains like our use case)
- improvements on analysis part
  - reordering of analysis steps to download each page just once  
    => every page is now downloaded just once max instead of max 3 times
  - filtering for file content and file encoding now with http header `Content-Type` & `Content-Encoding`
  - multiple adaptations in check page part

I tried to stay as close as possible to the original implementation and the description of the different steps in the paper.

## Usage
### From Source
Prerequisite:
Installed python with version >= 3.10  

Clone this repository with:  
```console
git clone https://github.com/ftjahn8/orphan-detection.git
```

Install required python modules with:  
```console
python -m pip install -r requirements.txt
```

Run main script with needed arguments:  
```console
python main.py [domain] [args]
```

### Docker
#### Build Docker File yourself#
Clone this repository with:
```console
git clone https://github.com/ftjahn8/orphan-detection.git
```

Build the Image
```console
docker build -t orphan-detection --rm .
```

Run the image as container
```console
docker run -v [absolute-path-to-target-directory]:/app/Data -it --name my_detection --rm orphan-detection [domain] [args]
```

Binding the output directory to your local machine:  
You can specify where the ```Data``` directory of your docker container should be mounted into your local systemin the docker argument ```-v [absolute-path-to-target-directory]:/app/Data```.
The ```Data``` directory contains all results & outputs of the processes and can have a size of multiple GB depending on how big your domain is and how many domains you have scanned already.

If you don`t need the output you can remove the ```-v``` from the docker command

## Instructions
### Potential Orphan Detection

Example command for execution the detection with some arguments (with source code):  
 ```console
python main.py example.com -d --lc 5 --min_subdomain_size 50 --probe_delay 0.5
```

Example command for execution the detection with some arguments (with docker container):  
 ```console
docker run  -it --name my_detection --rm orphan-detection example.com -d --lc 5 --min_subdomain_size 50 --probe_delay 0.5
```

Available Arguments and flags for the detection process:

| Argument                 | Description                                                                                                                                                        | Accepted Values                                            | Default Value                       | Example*                            |
|--------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------|-------------------------------------|-------------------------------------|
| -s                       | skip download phase and reuse already downloaded data from a previous run (date has to be of the previous download run!)                                           | date with the format YYYY-MM-DD                            | deactivated                         | -s 2022-06-26                       |
| -d                       | Use dynamic url detection (DUDe)                                                                                                                                   | -                                                          | deactivated                         | -d                                  |
| --current_sitemap_filter | Last seen dates for a page newer than the Date Value of the ``--current_sitemap_filter``<br> are discarded as still part of the domain                             | date with the format YYYY-MM-DD <br>or YYYY-MM <br>or YYYY | 1st of Jan in the year of execution | --current_sitemap_filter 2022-06-25 |
| --pc                     | Popularity cutoff (DUDe Parameter)                                                                                                                                 | decimal                                                    | 0.05                                | --pc 0.1                            |
| --st                     | Short-link cutoff (DUDe Parameter)                                                                                                                                 | decimal                                                    | 15                                  | --st 20                             |
| --lt                     | Long-link threshold (DUDe Parameter)                                                                                                                               | decimal                                                    | 20                                  | --lt 50                             |
| --lc                     | Long-link cutoff (DUDe Parameter)                                                                                                                                  | decimal                                                    | 0                                   | --lc 5                              |
| --min_subdomain_size     | Min amount of pages of a single subdomain to be filtered with DUDe. Subdomains with less pages are ignored for the Dude Step. (DUDe Parameter)                     | decimal                                                    | 40                                  | --min_subdomain_size 20             |
| --probe_delay            | Cooldown time (in sec) between two requests in the `probe`-step. Smaller values mean more requests per min to the domain / infrastructure.                         | decimal                                                    | 0.5 (sec)                           | --probe_delay 2.2                   |
| --probe_timeout          | Time (in sec) for a single request to timeout in the `probe`-step. Smaller values mean a higher potential to misinterpret a slow response as not running any more. | decimal                                                    | 5 (sec)                             | --probe_timeout 3.5                 |

*Example values are just for displaying how to declare them. They are no recommendations for your process runs.  
For further information on the Dude Parameter, have a look in the paper. There they are described in more detail.  
For further information on the -s & -d flags, have a look in the description of the original implementation.  

You can find the results of your run in ``Data/Results/[domain-name]/[domain-name]_potential_orphans.txt``.

### Analysis of Potential Orphans
! Requires the ``Potential Orphan Detection``-process to be finished as the analysis re-uses the detection outputs for its own input.  
! Requires the ``-a``-flag in the command, otherwise the detection process is started.

Example command for execution the detection with some arguments (with source code):  
 ```console
python main.py example.com -a --a_cpd_timeout 10 --a_lspd_timeout 10 --a_os_cutoff 0.9 
```

Example command for execution the detection with some arguments (with docker container):  
 ```console
docker run  -it --name my_detection --rm orphan-detection example.com -a --a_cpd_timeout 10 --a_lspd_timeout 10 --a_os_cutoff 0.9 
```

Available Arguments and flags for the detection process:

| Argument                 | Description                                                                                                                                                                                                                                                                                   | Accepted Values | Default Value | Example*                     |
|--------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------|---------------|------------------------------|
| -a                       | Activates the analysis process. Without this flag the detection process is started.                                                                                                                                                                                                           | -               | deactivated   | -a                           |
| --a_cpd_timeout          | Time (in sec) for a single request to timeout during the download of pages in its current state. Smaller values mean a higher potential to misinterpret a slow response as not running any more.                                                                                              | decimal         | 5             | --a_cpd_timeout 3            |
| --a_cpd_interval         | Time (in sec) between two requests to download pages in their current states. Smaller values mean more requests per min to the domain / infrastructure.                                                                                                                                       | decimal         | 1             | --a_cpd_interval 3           |
| --a_sf_epsilon           | Max size difference to identify two pages as the same.                                                                                                                                                                                                                                        | decimal         | 5             | --a_sf_epsilon 20            |
| --a_sf_min_amount        | Minimum amount of pages which have to have the "same" size (content) to be sorted out.                                                                                                                                                                                                        | decimal         | 2             | --a_sf_min_amount 5          |
| --a_lspd_timeout         | Time (in sec) for a single request to timeout during the download of pages in their last seen version.                                                                                                                                                                                        | decimal         | 5             | --a_lspd_timeout 10          |
| --a_lspd_interval        | Time (in sec) between two requests to the web archive to retrieve the page in its last seen version.<br> Be careful with this rate, the web archive is very sensitive for too much requests <br>and starts to not respond to new requests very quickly, <br>which ruins the analysis results. | decimal         | 1.5           | --a_lspd_interval 3          |
| --a_os_age_weight        | Weight for the age of a page in the orphan score calculation                                                                                                                                                                                                                                  | decimal         | 0.1           | --a_os_age_weight 0.3        |
| --a_os_similarity_weight | Weight for the similarity score in the open score calculation                                                                                                                                                                                                                                 | decimal         | 0.9           | --a_os_similarity_weight 0.7 |
| --a_os_cutoff            | Cutoff value for the orphan score to identify likely orphan page                                                                                                                                                                                                                              | decimal         | 0.7           | --a_os_cutoff 0.9            |

*Example values are just for displaying how to declare them. They are no recommendations for your process runs.  
For further information on the sf (size filter) and os (Orphan Score filter) parameters, have a look in the paper. There they are described in more detail.  
The results of the analysis can be found in ```Data/Results/[domain-name]/[domain-name]_analysis_results```.

### Language & Modules
- Python 3.10
- Python modules:
  - [requests](https://requests.readthedocs.io/en/latest/)
  - [beautifulsoup4](https://www.crummy.com/software/BeautifulSoup/)
  - [tqdm](https://tqdm.github.io/)
