from huggingface_hub import HfApi

api = HfApi()
api.create_repo("UCSB-SURFI/SeCodePLT-Juliet", exist_ok=True)
api.upload_large_folder(
    folder_path="./dataset",
    repo_id="UCSB-SURFI/SeCodePLT-Juliet",
    repo_type="dataset",
)
