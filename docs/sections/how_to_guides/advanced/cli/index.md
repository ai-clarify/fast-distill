# Command Line Interface (CLI)

`FastDistill` offers a [`CLI`][fastdistill.cli.pipeline.utils] to _explore_ and _re-run_ existing [`Pipeline`][fastdistill.pipeline.Pipeline] dumps, meaning that an existing dump can be explored to see the steps, how those are connected, the runtime parameters used, and also re-run it with the same or different runtime parameters, respectively.

## Available commands

The only available command as of the current version of `fastdistill` is `fastdistill pipeline`.

```bash
$ fastdistill pipeline --help

 Usage: fastdistill pipeline [OPTIONS] COMMAND [ARGS]...

 Commands to run and inspect FastDistill pipelines.

╭─ Options ───────────────────────────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                                             │
╰─────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ──────────────────────────────────────────────────────────────────────────────╮
│ info      Get information about a FastDistill pipeline.                                  │
│ run       Run a FastDistill pipeline.                                                    │
╰─────────────────────────────────────────────────────────────────────────────────────────╯
```

So on, `fastdistill pipeline` has two subcommands: `info` and `run`, as described below. Note that for testing purposes we will be using the following [dataset](https://huggingface.co/datasets/fastdistill-internal-testing/ultrafeedback-mini).

### `fastdistill pipeline info`

```bash
$ fastdistill pipeline info --help

 Usage: fastdistill pipeline info [OPTIONS]

 Get information about a FastDistill pipeline.

╭─ Options ───────────────────────────────────────────────────────────────────────────╮
│ *  --config        TEXT  Path or URL to the FastDistill pipeline configuration file. │
│                          [default: None]                                            │
│                          [required]                                                 │
│    --help                Show this message and exit.                                │
╰─────────────────────────────────────────────────────────────────────────────────────╯
```

As we can see from the help message, we need to pass either a `Path` or a `URL`. This second option comes handy for datasets stored in Hugging Face Hub, for example:

```bash
fastdistill pipeline info --config "https://huggingface.co/datasets/fastdistill-internal-testing/instruction-dataset-mini-with-generations/raw/main/pipeline.yaml"
```

If we take a look:

![CLI 1](../../../../assets/images/sections/cli/cli_pipe.png)

The pipeline information includes the steps used in the `Pipeline` along with the `Runtime Parameter` that was used, as well as a description of each of them, and also the connections between these steps. These can be helpful to explore the Pipeline locally.

### `fastdistill pipeline run`

We can also run a `Pipeline` from the CLI just pointing to the same `pipeline.yaml` file or an URL pointing to it and calling `fastdistill pipeline run`. Alternatively, an URL pointing to a Python script containing a fastdistill pipeline can be used:

```bash
$ fastdistill pipeline run --help

 Usage: fastdistill pipeline run [OPTIONS]

 Run a FastDistill pipeline.

╭─ Options ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --param                                          PARSE_RUNTIME_PARAM  [default: (dynamic)]                                         │
│ --config                                         TEXT                 Path or URL to the FastDistill pipeline configuration file.   │
│                                                                       [default: None]                                              │
│ --script                                         TEXT                 URL pointing to a python script containing a fastdistill      │
│                                                                       pipeline.                                                    │
│                                                                       [default: None]                                              │
│ --pipeline-variable-name                         TEXT                 Name of the pipeline in a script. I.e. the 'pipeline'        │
│                                                                       variable in `with Pipeline(...) as pipeline:...`.            │
│                                                                       [default: pipeline]                                          │
│ --ignore-cache              --no-ignore-cache                         Whether to ignore the cache and re-run the pipeline from     │
│                                                                       scratch.                                                     │
│                                                                       [default: no-ignore-cache]                                   │
│ --repo-id                                        TEXT                 The Hugging Face Hub repository ID to push the resulting     │
│                                                                       dataset to.                                                  │
│                                                                       [default: None]                                              │
│ --commit-message                                 TEXT                 The commit message to use when pushing the dataset.          │
│                                                                       [default: None]                                              │
│ --private                   --no-private                              Whether to make the resulting dataset private on the Hub.    │
│                                                                       [default: no-private]                                        │
│ --token                                          TEXT                 The Hugging Face Hub API token to use when pushing the       │
│                                                                       dataset.                                                     │
│                                                                       [default: None]                                              │
│ --help                                                                Show this message and exit.                                  │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

Using `--config` option, we must pass a path with a `pipeline.yaml` file.
To specify the runtime parameters of the steps we will need to use the `--param` option and the value of the parameter in the following format:

```bash
fastdistill pipeline run --config "https://huggingface.co/datasets/fastdistill-internal-testing/instruction-dataset-mini-with-generations/raw/main/pipeline.yaml" \
	--param load_dataset.repo_id=fastdistill-internal-testing/instruction-dataset-mini \
	--param load_dataset.split=test \
	--param generate_with_gpt35.llm.generation_kwargs.max_new_tokens=512 \
	--param generate_with_gpt35.llm.generation_kwargs.temperature=0.7 \
	--param to_argilla.dataset_name=text_generation_with_gpt35 \
	--param to_argilla.dataset_workspace=admin
```

Or using `--script` we can pass directly a remote python script (keep in mind `--config` and `--script` are exclusive):

```bash
fastdistill pipeline run --script "https://huggingface.co/datasets/fastdistill-internal-testing/pipe_nothing_test/raw/main/pipe_nothing.py"
```

You can also pass runtime parameters to the python script as we saw with `--config` option.

Again, this helps with the reproducibility of the results, and simplifies sharing not only the final dataset but also the process to generate it.

#### Layered YAML configs

You can apply environment/run overrides to a base pipeline YAML (deep-merged, lists replaced):

```bash
fastdistill pipeline run \
  --config configs/pipeline.yaml \
  --config-env configs/env/dev.yaml \
  --config-run configs/run/override.yaml
```

The same overlay flags are supported on `fastdistill pipeline info`.
