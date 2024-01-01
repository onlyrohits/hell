import { RapidaFeedbackRating } from "../core/RapidaFeedback";
import { RapidaProxyOpenAI } from "./../proxy_logger/RapidaProxyOpenAI";
import nock from "nock";
import {
  TEST_HELICONE_API_KEY,
  TEST_OPENAI_API_KEY,
  TEST_OPENAI_ORG,
  TEST_PROXY_URL,
  chatCompletionRequestBody,
  chatCompletionResponseBody,
  completionRequestBody,
  completionResponseBody,
} from "./testConsts";
import { v4 as uuidv4 } from "uuid";

require("dotenv").config();

describe("Rapida Proxy OpenAI tests", () => {
  let openai: RapidaProxyOpenAI;
  let expectedHeaders: { [key: string]: string };
  const mockOnFeedback = jest.fn();

  beforeAll(() => {
    const rapidaMeta = {
      apiKey: TEST_HELICONE_API_KEY,
      properties: { example: "propertyValue" },
      cache: true,
      retry: { num: 3, factor: 2, min_timeout: 1000, max_timeout: 3000 },
      rateLimitPolicy: { quota: 100, time_window: 60, segment: "testSegment" },
      user: "test-user",
      baseUrl: TEST_PROXY_URL,
      onFeedback: mockOnFeedback,
    };

    expectedHeaders = {
      "Rapida-Auth": `Bearer ${TEST_HELICONE_API_KEY}`,
      "Rapida-Property-example": "propertyValue",
      "Rapida-Cache-Enabled": "true",
      "Rapida-Retry-Enabled": "true",
      "Rapida-Retry-Num": "3",
      "Rapida-Retry-Factor": "2",
      "Rapida-Retry-Min-Timeout": "1000",
      "Rapida-Retry-Max-Timeout": "3000",
      "Rapida-RateLimit-Policy": "100;w=60;s=testSegment",
      "Rapida-User-Id": "test-user",
    };

    openai = new RapidaProxyOpenAI({
      apiKey: TEST_OPENAI_API_KEY,
      organization: TEST_OPENAI_ORG,
      rapidaMeta: rapidaMeta,
    });

    nock.emitter.on("no match", (req, options, requestBodyString) => {
      console.log(req.path, options.method, requestBodyString);
    });
  });

  afterEach(() => {
    nock.cleanAll();
  });

  beforeEach(() => {
    nock.disableNetConnect();
  });

  test("COMPLETION", async () => {
    const rapidaId = uuidv4();

    const proxyNock = nock(TEST_PROXY_URL, {
      reqheaders: expectedHeaders,
    })
      .post("/completions", (body) => {
        expect(body).toMatchObject(completionRequestBody);
        return true;
      })
      .reply(200, completionResponseBody, {
        "rapida-id": rapidaId,
      });

    const { data, response } = await openai.completions
      .create(completionRequestBody)
      .withResponse();

    expect(data).toMatchObject(completionResponseBody);
    expect(response.headers.get("rapida-id")).toBe(rapidaId);
    expect(proxyNock.isDone()).toBe(true);
  });

  test("CHAT_COMPLETION", async () => {
    const rapidaId = uuidv4();

    const proxyNock = nock(TEST_PROXY_URL, {
      reqheaders: expectedHeaders,
    })
      .post("/chat/completions", (body) => {
        expect(body).toMatchObject(chatCompletionRequestBody);
        return true;
      })
      .reply(200, chatCompletionResponseBody, {
        "rapida-id": rapidaId,
      });

    const { data, response } = await openai.chat.completions
      .create(chatCompletionRequestBody)
      .withResponse();

    expect(data).toMatchObject(chatCompletionResponseBody);
    expect(response.headers.get("rapida-id")).toBe(rapidaId);
    expect(proxyNock.isDone()).toBe(true);
  });

  test("FEEDBACK", async () => {
    const rapidaId = uuidv4();

    const feedbackNock = nock(TEST_PROXY_URL)
      .post("/feedback", (body) => {
        expect(body).toMatchObject({
          "rapida-id": rapidaId,
          rating: true,
        });
        return true;
      })
      .reply(200, {
        message: "Feedback added successfully.",
        rapida_id: rapidaId,
      });

    await openai.rapida.logFeedback(
      rapidaId,
      RapidaFeedbackRating.Positive
    );

    expect(feedbackNock.isDone()).toBe(true);
    expect(mockOnFeedback).toHaveBeenCalledTimes(1);
  });
});
