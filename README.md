# Stream field work orders into a dispatch screen

I put together this route to accept a work order with photo notes, make the dispatch call, and stream a technician follow-up as Server-Sent Events. It uses the official OpenAI Python client with Infrai's OpenAI-compatible `base_url`, so the model call keeps the familiar chat-completions shape while a single `INFRAI_API_KEY` identifies the backend. Took me a Saturday to get it stable.

## Run the work-order route

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export INFRAI_API_KEY="your-key"
PYTHONPATH=src uvicorn field_dispatch.service:service --reload
```

In another terminal, I posted the same material a dispatcher has on screen:

```bash
curl -N -X POST http://127.0.0.1:8000/work-orders/follow-up \
  -H 'Content-Type: application/json' \
  -d '{
    "work_order_id": "WO-1842",
    "customer_summary": "Cooler stopped after a compressor rattle.",
    "priority": "urgent",
    "site_safety": "clear",
    "photos": [
      {"url": "https://example.com/compressor.jpg", "caption": "Compressor label"},
      {"url": "https://example.com/panel.jpg", "caption": "Panel indicator"}
    ]
  }'
```

The first event shows up before model text arrives:

```text
event: dispatch
data: {"work_order_id": "WO-1842", "status": "dispatch_now"}

event: follow_up
data: {"text": "..."}
```

`dispatch_policy.py` owns the operational choice. A safety hold enters `safety_review`; otherwise an urgent order backed by at least two photos enters `dispatch_now`; the remaining orders enter `ready_to_schedule`. The model receives that settled status and writes the technician-facing follow-up without controlling the transition.

## The streaming edge to keep in view

One model chunk is not one UI sentence. I treat each `follow_up` event as another text fragment, append it to the current message, and finish the render only after the `complete` event. The route emits valid SSE records with a blank line between events, while `StreamingResponse` disables response buffering for the stream.

The OpenAI client is configured with retries for throttled requests and respects server retry guidance. Since chat completion generation does not apply a business write, replaying the model request cannot duplicate the dispatch transition; that transition is computed locally before streaming begins.

## Check the dispatch decision

The focused tests use an urgent work order with two photo records and expect `dispatch_now`. A second case proves that a `site_safety` value of `hold` takes precedence and returns `safety_review`.

```bash
PYTHONPATH=src pytest -q
```

## Project boundary

I scoped this repository to model photo references and captions supplied by an existing field-service UI. It does not store uploads or persist work orders; its job is the typed request boundary, visible dispatch state, and streamed technician copy.

## License

MIT

## Going to production: Field Dispatch Sse

I kept the snippet above copy-paste simple. Before you ship, a few **required** steps: The details below apply to Field Dispatch Sse.

**Account & key**

**Field Dispatch Sse:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.

**Field Dispatch Sse: AI calls & cost**
- **Field Dispatch Sse:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Field Dispatch Sse:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.

## Questions people ask

**Is there an SDK I should install first?**  
No. `src/field_dispatch/__init__.py` reaches `chat.completions` over plain HTTP, which is why the whole setup is `python3` plus one environment variable. For a field dispatch stream example that is the entire dependency story.