# Sound Cue Sheet

Turn timed audio events into a mix cue sheet with competing sounds and peak voice counts.

**[Open the live demo](https://oguzhanozfe.github.io/sound-cue-sheet/)** · [Browser features and setup](demo/DEMO.md)

![Sound Cue Sheet showing the included example in the browser](docs/preview.png)

[Deploy to Render](https://render.com/deploy?repo=https://github.com/oguzhanozfe/sound-cue-sheet) · [Example input](example.json) · [Computed report](docs/example-report.json) · [Model settings](#connect-a-model)

## Try it

With Python 3.11 or newer, run:

```sh
git clone https://github.com/oguzhanozfe/sound-cue-sheet.git
cd sound-cue-sheet
python app.py
```

Open **http://127.0.0.1:8000**. The example is already loaded. Choose **Input JSON** to edit it or open your own file, then **Run analysis**. **Export report** saves the computed evidence as JSON. The example works on a CPU with no dependencies, accounts or API keys.

## What the example shows

A designer logs a latch, pickup chime, radio warning and alarm over a room-tone bed. On paper every sound has a purpose. On the timeline, two high-priority cues compete during the warning. Sound Cue Sheet turns the event list into a practical listening pass for the mixer.

Each cue has a unique ID, start and duration in seconds, a bus label and a priority from 1 (background) to 5 (most important). The sheet lists cues in playback order. It names higher-priority cues to leave space for and equal-priority overlaps to balance by ear. Priority comparisons reach across buses because dialogue and effects can compete even when routed separately. A sweep of all start and end times measures the actual peak voice count. Adjacent cues do not overlap.

The cue sheet uses scheduled timing and declared priority. It does not measure sound levels, frequency masking, loudness targets or the character of a mix. The source material remains on the editor's machine.

**Sample result:** 6 cues produce 7 overlapping pairs, with up to 3 active at once.

## Run without a browser

```sh
python app.py analyze example.json
python -m unittest discover -v
```

The CLI writes JSON to stdout. The HTTP interface accepts `POST /api/analyze` with content type `application/json` and body `{"input": {...}, "review": false}`. The input object has the same shape as [example.json](example.json). `GET /api/example` returns a complete working request input and report. `GET /health` is the deployment health check.

## Connect a model

Analysis always computes the measurements locally. To add an English review of those measurements, select a provider on the **server**, set its variables and restart. `MODEL_PROVIDER=off` is the default.

| Provider | Configuration |
| --- | --- |
| Local (Ollama, LM Studio, llama.cpp) | `MODEL_PROVIDER=local`, `MODEL_ID=<installed chat model>`, `MODEL_BASE_URL=http://127.0.0.1:11434/v1` (Ollama) or `http://127.0.0.1:1234/v1` (LM Studio). |
| Azure OpenAI | `MODEL_PROVIDER=azure`, `MODEL_ID=<deployment name>`, `MODEL_BASE_URL=https://<resource>.openai.azure.com/openai/v1`, `MODEL_API_KEY=<resource key>`. |
| AWS Bedrock | `MODEL_PROVIDER=bedrock`, `MODEL_ID=<Converse-compatible model or inference profile ID>`, `AWS_REGION=<region>`. Use an AWS role or the standard SDK credential chain with permission to invoke that model. Install `requirements.txt` when running outside Docker. |
| OpenAI or compatible hosted API | `MODEL_PROVIDER=api`, `MODEL_BASE_URL=https://<provider>/v1`, `MODEL_ID=<chat model>`, `MODEL_API_KEY=<key>`. The default API root is `https://api.openai.com/v1`. |

For example, with a running local model (Bash):

```sh
MODEL_PROVIDER=local MODEL_ID=your-model MODEL_BASE_URL=http://127.0.0.1:1234/v1 python app.py analyze example.json --review
```

On PowerShell set each variable with `$env:MODEL_ID = "your-model"` (and likewise for the provider and base URL) before running `python app.py analyze example.json --review`. Model output is a separate `model_review` field. The model receives the summary, metrics and a bounded sample of result rows. An optional review with a hosted provider sends that evidence to the configured provider.

## Deploy

The Render link uses [render.yaml](render.yaml) to deploy the included Dockerfile. Select the new service and deploy. An account is required on the hosting platform. To run the same container locally:

```sh
docker build -t sound-cue-sheet .
docker run --rm -p 127.0.0.1:8000:8000 sound-cue-sheet
```

The container honors `PORT` (default 8000). Add provider variables through the host's secret settings or Docker's `--env-file`. For browser model reviews on a deployment, also set a long `MODEL_ACCESS_TOKEN` and enter it in **Model review**. The server keeps provider credentials out of the browser. To reach a model on the Docker host, use a reachable host address instead of container loopback; Docker Desktop provides `host.docker.internal`.

The deterministic analysis lives in [project.py](project.py). Provider adapters are in [providers.py](providers.py). [MIT license](LICENSE).
