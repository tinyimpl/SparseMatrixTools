# Sparse-Matrix-Tools
## Description
- [x] plot.py: draw images of sparse matrix 
- [x] meta_info.py: show meta info of sparse matrix
- [x] download.py: download sparse matrix from [sparse market](https://sparse.tamu.edu/)
- [x] read.py: read the sparse matrix for the specified row or index
- [ ] transform.py: format conversion of sparse matrix

## Run
```bash
# install poetry
curl -sSL https://install.python-poetry.org | python3 -
# install dependencies
poetry install
# run plot
poetry run python3 ./src/plot.py --format ${Matrix Format} --file ${Matrix File}
# run meta_info
poetry run python3 ./src/meta_info.py --format ${Matrix Format} --file ${Matrix File}
# run download
poetry run python3 ./src/download.py
> 1. search
> 2. append
> 3. list
> 4. remove
> 5. download
# run read
poetry run python3 ./src/read.py --format ${Matrix Format} --file ${Matrix File} --to ${Read Format}
> 1. row -> r -i idx
> 2. col -> c -i idx
> 3. val -> v -i idx
```

