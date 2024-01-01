import { RapidaAsyncOpenAI } from "../async_logger/RapidaAsyncOpenAI";
import { Response } from "openai/core";
import { RapidaFeedbackRating } from "../core/RapidaFeedback";
import { RapidaProxyOpenAI } from "../proxy_logger/RapidaProxyOpenAI";
import * as dotenv from "dotenv";

dotenv.config();

async function testAsync(): Promise<void> {
  const openai = new RapidaAsyncOpenAI({
    apiKey: process.env.OPENAI_API_KEY,
    organization: process.env.OPENAI_ORG_ID,
    rapidaMeta: {
      apiKey: process.env.HELICONE_API_KEY,
      baseUrl: "https://api_staging.hconeai.com",
      onLog: async (response: Response) => {
        console.log(`Log result: ${response.status}`);
        const rapidaId = response.headers.get("rapida-id");
        if (rapidaId) {
          await openai.rapida.logFeedback(
            rapidaId,
            RapidaFeedbackRating.Positive
          );
        }
      },
      onFeedback: async (response: Response) => {
        console.log(`Feedback result: ${response.status}`);
      },
    },
  });

  const data = await openai.chat.completions.create({
    model: "gpt-3.5-turbo",
    messages: [
      {
        role: "user",
        content: "Say 'TestAsync_ChatCompletion_NoStreaming'",
      },
    ],
  });

  console.log(data.choices[0].message.content);

  const { data: dataStreaming, response: responseStreaming } =
    await openai.chat.completions
      .create(
        {
          model: "gpt-3.5-turbo",
          messages: [
            {
              role: "user",
              content: "Say what up",
            },
          ],
          stream: true,
        },
        { stream: true }
      )
      .withResponse();

  const chunks: string[] = [];

  for await (const chunk of dataStreaming) {
    chunks.push(chunk.choices[0].delta.content ?? "");
  }

  console.log(`Streaming result: ${chunks.join("")}`);

  const { data: data2, response: response2 } = await openai.completions
    .create({
      model: "davinci",
      prompt: "1+1=",
    })
    .withResponse();

  console.log(data2.choices[0].text);

  const { data: data3, response: response3 } = await openai.embeddings
    .create({
      input: "Hello, world!",
      model: "text-embedding-ada-002",
    })
    .withResponse();

  console.log(data3.data[0].embedding); // Ugly, but works

  return;
}

async function testProxy(): Promise<void> {
  const openai = new RapidaProxyOpenAI({
    apiKey: process.env.OPENAI_API_KEY,
    organization: process.env.OPENAI_ORG_ID,
    rapidaMeta: {
      apiKey: process.env.HELICONE_API_KEY,
      onFeedback: async (response: Response) => {
        console.log(`Feedback result: ${response.status}`);
      },
    },
  });

  const { data, response } = await openai.chat.completions
    .create({
      model: "gpt-3.5-turbo",
      messages: [
        {
          role: "user",
          content: "Say 'TestProxy_ChatCompletion_NoStreaming'",
        },
      ],
    })
    .withResponse();

  console.log(data.choices[0].message.content);

  const rapidaId = response.headers.get("rapida-id");
  if (rapidaId) {
    await openai.rapida.logFeedback(
      rapidaId,
      RapidaFeedbackRating.Negative
    );
  }
}

function withTimeout(promise: any, ms: any) {
  return new Promise((resolve, reject) => {
    const timeout = setTimeout(() => {
      reject(new Error("Promise timed out"));
    }, ms);

    promise
      .then((response: any) => {
        clearTimeout(timeout);
        resolve(response);
      })
      .catch((error: any) => {
        clearTimeout(timeout);
        reject(error);
      });
  });
}

withTimeout(testAsync(), 10000)
  .then(() => {
    console.log("test() completed");
  })
  .catch((error) => {
    console.log("test() failed:", error);
  });

withTimeout(testProxy(), 5000)
  .then(() => {
    console.log("testProxy() completed");
  })
  .catch((error) => {
    console.log("testProxy() failed:", error);
  });