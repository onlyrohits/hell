import { Rapida } from "../core/RapidaOpenAIApi";
import OpenAI from "openai";
import * as Core from "openai/core";
import { RapidaHeaderBuilder } from "../core/RapidaHeaderBuilder";
import {
  IRapidaMeta,
  IRapidaProxyClientOptions,
} from "../core/RapidaClientOptions";

export class RapidaProxyOpenAI extends OpenAI {
  public rapida: Rapida;
  private rapidaHeaders: { [key: string]: string };

  constructor(private options: IRapidaProxyClientOptions) {
    const {
      apiKey,
      organization,
      rapidaMeta: providedRapidaMeta = {},
      ...opts
    } = options;

    const rapidaMeta: IRapidaMeta = {
      ...providedRapidaMeta,
      apiKey: providedRapidaMeta.apiKey || Core.readEnv("HELICONE_API_KEY"),
      baseUrl: providedRapidaMeta.baseUrl || "https://oai.hconeai.com/v1",
    };

    super({
      apiKey,
      organization,
      baseURL: rapidaMeta.baseUrl,
      ...opts,
    });

    this.rapida = new Rapida(rapidaMeta);
    this.rapidaHeaders = new RapidaHeaderBuilder(rapidaMeta)
      .withPropertiesHeader()
      .withCacheHeader()
      .withRetryHeader()
      .withRateLimitPolicyHeader()
      .withUserHeader()
      .build();
  }

  protected override defaultHeaders(
    opts: Core.FinalRequestOptions
  ): Core.Headers {
    return {
      ...super.defaultHeaders(opts),
      ...this.rapidaHeaders,
    };
  }
}
