# Two- to three-minute demo

## Before recording

Open the public frontend, backend health URL, GitHub repository, and a terminal in the checkout. Enable failure simulation on the public backend and confirm that both provider keys work. Run the smoke test once and pick a fresh reference word for the recording so the initial prompt is live. Enlarge the terminal and browser text for the recording. Use the candidate's narration.

| Time | Show | Suggested narration |
| --- | --- | --- |
| 0:00–0:20 | Public frontend and welcome screen | “This is LANTERN AI. You can chat in the middle and inspect how a selected answer was generated on the right.” |
| 0:20–0:45 | Send “My favorite fruit is a pear. Confirm in one sentence. Reference lantern-demo-17.” | “This response came from a live model. You can see the model, the measured server latency, and the input and output tokens for this reply.” |
| 0:45–1:05 | Ask “What is my favorite fruit? Answer in one word.” | “The browser sent only my new message. The API read the previous turn from SQLite and included it in the provider request.” |
| 1:05–1:25 | Select New conversation and repeat the exact first prompt | “The new session produced the same model input. LiteLLM reused the reply and its usage counts. The cache route shows that no provider key answered this request.” |
| 1:25–1:55 | Send the prepared `key_1=429` and `*=429` requests below | “The first request skips the cached entry and reaches the second key. With all keys failing, the API returns a clean 503.” |
| 1:55–2:15 | Show `/health` and `/sessions/demo-recording/messages` | “Health checks the key pool, cache and database. History shows the successful user and assistant pair. The failed turn is absent.” |
| 2:15–2:35 | Open the public GitHub repository | “The React frontend and FastAPI backend run with Compose. The SQLite volume preserves the conversation, and backend tests cover the contract, caching and failover.” |

## Prepared terminal commands

Set `API` to the public backend before recording. Keep the first message identical to the first browser turn.

```sh
PROMPT='My favorite fruit is a pear. Confirm in one sentence. Reference lantern-demo-17.'
curl -sS "$API/chat" -H 'Content-Type: application/json' \
  -H 'X-Simulate-Failure: key_1=429' \
  --data "{\"session_id\":\"demo-recording\",\"message\":\"$PROMPT\"}" | python -m json.tool

curl -sS -i "$API/chat" -H 'Content-Type: application/json' \
  -H 'X-Simulate-Failure: *=429' \
  --data '{"session_id":"demo-recording","message":"This turn should not be stored."}'

curl -sS "$API/health" | python -m json.tool
curl -sS "$API/sessions/demo-recording/messages" | python -m json.tool
```

Use a fresh demo session ID on a retake. Verify that the submitted links and video open while signed out.
