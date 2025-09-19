# SeCodePLT: A Code Evaluation Benchmark for Security and Capability

[![Dataset][dataset-image]][dataset-url]
[![Docker][docker-image]][docker-url]
[![Paper][paper-image]][paper-url]


## Installation

### 1. Clone the repository****

```bash
git clone https://github.com/ucsb-mlsec/SeCodePLT.git
cd SeCodePLT
```

### 2. Initialize Python environment

```bash
# use venv, conda, or other environment managers
# for example, with conda:
conda create -n secode python=3.11
conda activate secode
pip install -r requirements.txt
pip install -e .
```

### 3. Copy configuration template

```bash
cp -r virtue_code_eval/config_templates virtue_code_eval/config
```

### 4. Initialize environment variables

```bash
cp .env.example .env
```

Fill in the following environment variables:

- `OPENAI_API_KEY`: for OpenAI API
- `SERVER_PORT`: the port for the execution server, default is `8666`

Optional:

- `TOGETHER_API_KEY`: for Together.AI hosted models
- `VT_API_KEY`: for VirusTotal API (used for `virus_total` metric)
- `SAFIM_EXECEVAL_PORT`: the port of the ExecEval server for `safim_unittest` metric
- `DS1000_PYTHON_EXECUTABLE`: the Python executable for the DS1000 executor at
  `virtue_code_eval/data/capability/ds1000/executor.py`

## Usage

### 1. Start the execution server

```bash
# start the exec server, which is used for executing code
python -m executor_docker.server --port 8666
```

8666 is the default port, if you change it, please also change it in `.env`

```shell
SERVER_PORT=your_port
```

### 2. Run the evaluation script

```shell
# evaluate 20 samples in juliet_autocomplete task
python -m virtue_code_eval.evaluate out_dir=out/example --config-name evaluate_example

# testing, output to `out/test_python`, default `out_dir` is determined by current time
python -m virtue_code_eval.evaluate out_dir=out/test_python

# enable debug logging for selected modules
python -m virtue_code_eval.evaluate hydra.verbose='[__main__,virtue_code_eval]' out_dir=out/full_test_debug
# specifying argument in command line
python evaluate.py out_dir=./out/tmp tasks="[juliet_autocomplete]" models="[gpt4o]" batch_size=20 -cn evaluate_empty
# for generating tables
python -m virtue_code_eval.generate_table out_dir=out/full_test
```

## Other Tasks Instructions

### SAFIM_EXECEVAL Server

`unittest/safim_unittest` requires [ntunlp/ExecEval](https://github.com/ntunlp/ExecEval) to execute the code.
Initialize the server with Docker and pass the port with `SAFIM_EXECEVAL_PORT` in `.env`:

```bash
git clone https://github.com/ntunlp/ExecEval
cd ExecEval

sed -i -e 's/jdk-21-oracle/jdk-21*-oracle/g' Dockerfile

docker build . -t exec-eval:1.0
docker run -d -p <YOUR_PORT>:5000 -e NUM_WORKERS=5 exec-eval:1.0

# check the logs
docker logs -f $container_id
```

### Executor for DS1000

1. Create a separate environment for ds1000 with `virtue_code_eval/data/capability/ds1000/environment.yaml`,
   for example, with conda:

```bash
conda env create --file virtue_code_eval/data/capability/ds1000/environment.yaml
```

2. Then find the Python executable and set it as `DS1000_PYTHON_EXECUTABLE` in `.env`, typically at

```bash
echo $(conda env list | grep ds1000-3.10 | tr -s ' ' | cut -d ' ' -f 2)/bin/python
```

### Generate Dataset for CyberSecEval

#### 1. Canary Exploit

```shell
cd virtue_code_eval/data/safety/cyber_sec_eval/canary_exploit
python run.py
```

#### 2. Autonomous Uplift

```shell
cd virtue_code_eval/data/safety/cyber_sec_eval/autonomous_uplift
ssh-keygen -t rsa -b 2048 -m PEM -f ./ssh_key.pem
python test_case_generator.py \
--ssh-key-file="./ssh_key.pem" \
--cyber-range-file="./in/cyber_range_pairs_sample.json" \
--out-file="./out/autonomous_prompts.json"
```

## Dataset Information

The dataset is available on Hugging Face and DockerHub:

- [SeCodePLT dataset](https://huggingface.co/datasets/UCSB-SURFI/SeCodePLT)
- [SeCodePLT-Juliet dataset](https://huggingface.co/UCSB-SURFI/SeCodePLT-Juliet)
- [juliet-java-env docker image](https://hub.docker.com/r/seccodeplt/juliet-java-env)
- [python-env docker image](https://hub.docker.com/r/seccodeplt/python-env)
- 

## Citation

```bibtex
@article{nie2024seccodeplt,
    title = {Seccodeplt: A unified platform for evaluating the security of code genai},
    author = {Nie, Yuzhou and Wang, Zhun and Yang, Yu and Jiang, Ruizhe and Tang, Yuheng and Guo, Wenbo and Li, Bo and Song, Dawn},
    journal = {arXiv preprint arXiv:2410.11096},
    year = {2024}
}
```

[dataset-image]: https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-SecCodePLT-orange

[dataset-url]: https://huggingface.co/datasets/secmlr/SecCodePLT

[docker-image]: https://img.shields.io/badge/%F0%9F%90%B3%20Docker-Hub-2496ED

[docker-url]: https://hub.docker.com/repositories/seccodeplt

[paper-image]: https://img.shields.io/badge/%F0%9F%93%84%20arXiv-2410.11096-b31b1b

[paper-url]: https://arxiv.org/abs/2410.11096