# Rapida OpenAI v4+ Node.js Library

This package is a simple and convenient way to log all requests made through the OpenAI API with Rapida. You can easily track and manage your OpenAI API usage and monitor your GPT models' cost, latency, and performance on the Rapida platform.

## Proxy Setup

### Installation and Setup

1. **To get started, install the `rapida-openai` package**:

   ```bash
   npm install @rapida/rapida
   ```

2. **Set HELICONE_API_KEY as an environment variable:**

   ```base
   Set HELICONE_API_KEY as an environment variable:
   ```

   ℹ️ You can also set the Rapida API Key in your code (See below).

3. **Replace:**

   ```typescript
   const { ClientOptions, OpenAI } = require("openai");
   ```

   **with:**

   ```typescript
   const { RapidaProxyOpenAI as OpenAI,
       IRapidaProxyClientOptions as ClientOptions } = require("rapida");
   ```

4. **Make a request**
   Chat, Completion, Embedding, etc usage is equivalent to OpenAI package.

   ```typescript
   const openai = new OpenAI({
     apiKey: process.env.OPENAI_API_KEY,
     rapidaMeta: {
       apiKey: process.env.HELICONE_API_KEY, // Can be set as env variable
       // ... additional rapida meta fields
     },
   });

   const chatCompletion = await openai.chat.completion.create({
     model: "gpt-3.5-turbo",
     messages: [{ role: "user", content: "Hello world" }],
   });

   console.log(chatCompletion.data.choices[0].message);
   ```

### Send Feedback

Ensure you store the rapida-id header returned in the original response.

```typescript
const { data, response } = await openai.chat.completion
  .create({
    model: "gpt-3.5-turbo",
    messages: [{ role: "user", content: "Hello world" }],
  })
  .withResponse();

const rapidaId = response.headers.get("rapida-id");

await openai.rapida.logFeedback(rapidaId, RapidaFeedbackRating.Positive); // or Negative
```

### RapidaMeta options

```typescript
interface IRapidaMeta {
  apiKey?: string;
  properties?: { [key: string]: any };
  cache?: boolean;
  retry?: boolean | { [key: string]: any };
  rateLimitPolicy?: string | { [key: string]: any };
  user?: string;
  baseUrl?: string;
  onFeedback?: OnRapidaFeedback; // Callback after feedback was processed
}

type OnRapidaLog = (response: Response) => Promise<void>;
type OnRapidaFeedback = (result: Response) => Promise<void>;
```

### Advanced Features Example

```typescript
const options = new IRapidaProxyClientOptions({
  apiKey,
  rapidaMeta: {
    apiKey: process.env.HELICONE_API_KEY,
    cache: true,
    retry: true,
    properties: {
      Session: "24",
      Conversation: "support_issue_2",
    },
    rateLimitPolicy: {
      quota: 10,
      time_window: 60,
      segment: "Session",
    },
  },
});
```

## Async Setup

### Installation and Setup

1. **To get started, install the `rapida-openai` package**:

   ```bash
   npm install @rapida/rapida
   ```

2. **Set HELICONE_API_KEY as an environment variable:**

   ```base
   Set HELICONE_API_KEY as an environment variable:
   ```

   ℹ️ You can also set the Rapida API Key in your code (See below).

3. **Replace:**

   ```typescript
   const { ClientOptions, OpenAI } = require("openai");
   ```

   **with:**

   ```typescript
   const { RapidaAsyncOpenAI as OpenAI,
       IRapidaAsyncClientOptions as ClientOptions } = require("rapida");
   ```

4. **Make a request**
   Chat, Completion, Embedding, etc usage is equivalent to OpenAI package.

   ```typescript
   const openai = new OpenAI({
     apiKey: process.env.OPENAI_API_KEY,
     rapidaMeta: {
       apiKey: process.env.HELICONE_API_KEY, // Can be set as env variable
       // ... additional rapida meta fields
     },
   });

   const chatCompletion = await openai.chat.completion.create({
     model: "gpt-3.5-turbo",
     messages: [{ role: "user", content: "Hello world" }],
   });

   console.log(chatCompletion.data.choices[0].message);
   ```

### Send Feedback

With Async logging, you must retrieve the `rapida-id` header from the log response (not LLM response).

```typescript
const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
  rapidaMeta: {
    apiKey: process.env.HELICONE_API_KEY,
    onLog: async (response: Response) => {
      const rapidaId = response.headers.get("rapida-id");
      await openai.rapida.logFeedback(
        rapidaId,
        RapidaFeedbackRating.Positive
      );
    },
  },
});
```

### RapidaMeta options

Async logging loses some additional features such as cache, rate limits, and retries

```typescript
interface IRapidaMeta {
  apiKey?: string;
  properties?: { [key: string]: any };
  user?: string;
  baseUrl?: string;
  onLog?: OnRapidaLog;
  onFeedback?: OnRapidaFeedback;
}

type OnRapidaLog = (response: Response) => Promise<void>;
type OnRapidaFeedback = (result: Response) => Promise<void>;
```

&nbsp;

---

&nbsp;

> For more information see our [documentation](https://docs.rapida.ai/introduction).
