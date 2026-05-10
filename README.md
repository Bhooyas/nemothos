# Nemothos

![Nemothos](https://socialify.git.ci/Bhooyas/nemothos/image?font=KoHo&language=1&name=1&owner=1&pattern=Circuit%20Board&stargazers=1&theme=Auto)

A repository trying to replicate Mythos model type performance using NVIDIA Nemotron Models. The repository aims to find security and performace vulnerabilites in the code and optimize it.

## Running the model

The first step would be to clone the project using the following command: -
```bash
git clone https://github.com/Bhooyas/nemothos.git
```

The next step is to install the requirements for the project. We do that using the following command: -
```bash
cd nemothos
pip install -r requirements.txt
```

The next would be to install [Ollama](https://ollama.com/) and login into it using following command: -
```bash
ollama signin
```

Post this you can pass on any script and run the optimize it. We have provided a [test.py](test.py) on which you can experiment.
```bash
python main.py --file test.py
```

Alternatively you can even ask it to write the code and then optimize it.
```bash
python main.py --task "Write fastapi application with sql login and rate limiting"
```

The possible args of the file are:
```bash
Options:
  -m, --max-generation INTEGER  Number of times to run the loop
  --hard                        Use higher model and optimize harder
  --reasoning BOOLEAN           Use model with reasoning
  -f, --file FILE               Path of the file to optimize
  -t, --task TEXT               Task to write code for
  --run-id TEXT                 Run id to store details
  --help                        Show this message and exit.
```

The defualt model uses `nemotron-3-nano:30b-cloud`. We can also use `nemotron-3-super:cloud` by passing the `--hard` option.

**Note**: Based on our observations using `nemotron-3-nano:30b-cloud` for 3-5 generations works the best. Also it works across multiple languages.
