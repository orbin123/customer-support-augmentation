# Customer support walkthrough

A 73-second, silent walkthrough with explanatory text, recorded in Google Chrome on 3 November 2026. It uses the real application and a real email exchange between the two owner-provided Gmail accounts.

| Time | Scene |
| --- | --- |
| 00:00 | The customer's paddle-board sizing question |
| 00:07 | The query arrives in the integrated support mailbox |
| 00:12 | The support mailbox shows the generated reply and `ai-processed` label |
| 00:20 | The customer receives the reply in the original thread |
| 00:29 | The dashboard's saved inbound and outbound messages |
| 00:39 | Knowledge-base sizing facts |
| 00:47 | Included accessories and the editable knowledge base |
| 00:54 | Processing events |
| 01:01 | The supplied Pydantic Evals screenshot |

The demo question asks which paddle board suits a 90 kg rider on calm water and what accessories are included. The agent recommended the 11-foot All-round and listed the included equipment. Database verification identified ticket **102** (`answered`, `paddle-boards`) and event **137** (`processed`, one attempt, `action=reply`). No human escalation was needed.

## Editing and provenance

The native recording applications timed out during setup. Chrome captures were recorded through the browser screenshot interface with capture timestamps, then encoded at 24 fps. Mailbox and dashboard viewing clips retain their captured durations. The compose view, received-message view, event view, and supplied evaluation screenshot are explicit still inserts held for reading. Waiting time and setup attempts are omitted. This is an edited screen walkthrough, not an uninterrupted real-time recording. Unrelated ticket rows are masked in the exported video.

On-screen text explains the implementation; it is not a transcript of hidden model reasoning or a live planning interface. The present Events UI does not show tool calls or the stored final decision body. The screenshot's 91.7% is the historical average of section/action assertions, not overall answer accuracy.

The video contains no voiceover or music. Encoded chapter frames and the complete video decode were checked. No audio review applies.

## Rebuild the edit

The committed MP4, poster, evaluation screenshot, timeline, and renderer are the distributable artifacts. Original browser captures are retained locally under ignored `media/source/` because they include unrelated private mailbox content. They are not published with the repository.

With the local captures present, Pillow, FFmpeg, and Arial installed:

```bash
uv run --with pillow python media/render_demo.py
```

The renderer uses Python/Pillow for layout and redaction, and FFmpeg for H.264 MP4 encoding. `timeline.json` records the final scene times, captions, and source types. To rebuild on another machine, provide your own captures in the same manifest format and update the font path.
