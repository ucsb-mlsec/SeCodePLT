```shell
cd executor_docker
```
## install dependencies

```shell
pip install -r requirements.txt
```

## update juliet dataset (if you updated the dataset)

```shell
cd docker/juliet-java-env
python update_dataset.py
```

## update seccodeplt json dataset

```shell
python convert_dataset_to_json.py
python upload_to_huggingface.py
```

## update docker image

```shell
cd docker/juliet-java-env
# if there are updates from the dataset, run this command to update the dataset
huggingface-cli download secmlr/SecCodePLT-Juliet --repo-type dataset --local-dir ./dataset
# build docker locally
docker build -t juliet-java-env:latest .
# upload to Docker Hub
docker tag juliet-java-env:latest seccodeplt/juliet-java-env:latest
docker push seccodeplt/juliet-java-env:latest
```

## run testing

```shell
cd docker/juliet-java-env

# build docker locally
huggingface-cli download secmlr/SecCodePLT-Juliet --repo-type dataset --local-dir ./dataset
docker build -t juliet-java-env:latest .
# pull from Docker Hub
docker pull seccodeplt/juliet-java-env:latest
# run docker
cd ..
python -m server --host 127.0.0.1 --port 8666 --image juliet-java-env:latest

# some simple testing
cd ..
python evaluate.py out_dir=./out/tmp tasks="[juliet_autocomplete]" models="[gpt4o]" batch_size=20 -cn evaluate_small
```