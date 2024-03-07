if [[ $# -eq 0 ]] ; then
  echo 'File path is a mandatory positional argument'
  exit 1
fi

export FILE_PATH_TO_SERVE="$1"
poetry run uvicorn src.main:app --reload
