import { IRapidaAsyncClientOptions } from "../core/RapidaClientOptions";
import { Rapida } from "../core/RapidaOpenAIApi";
import {
  RapidaAsyncLogger,
  RapidaAsyncLogRequest,
  Provider,
} from "./RapidaAsyncLogger";
import { v4 as uuidv4 } from "uuid";

export interface RequestBody {
  model: string;
  provider?: string;
  prompt?: string;
  max_tokens?: number;
  temperature?: number;
  top_p?: number;
  n?: number;
  stream?: boolean;
  logprobs?: number;
  stop?: string[];
  presence_penalty?: number;
  frequency_penalty?: number;
  best_of?: number;
  logit_bias?: Record<string, number>;
  meta?: Object;
}

export interface Usage {
  total_tokens: number;
  prompt_tokens: number;
  completion_tokens: number;
}

export interface ResponseBody {
  text: string;
  usage?: Usage;
  index?: number;
  finish_reason?: string;
  logprobs?: Record<string, any>;
  chosen_logprobs?: Record<string, any>;
  tokens?: string[];
  token_logprobs?: number[];
  text_offset?: number;
  context?: string;
  model?: string;
  meta?: Object;
}

export interface ResponseError {
  error: string;
  status?: number;
  body?: Object;
}

export type RapidaResponse = ResponseError | ResponseBody;

export class RapidaLogBuilder {
  private response: RapidaResponse | undefined;
  private startTime: number;
  private endTime: number;
  private meta: Record<string, string>;
  public readonly id: string;

  constructor(private RequestBody: RequestBody) {
    this.startTime = Date.now();
    this.meta = {};
    this.id = uuidv4();
  }

  addResponse(response: RapidaResponse): RapidaLogBuilder {
    this.response = response;
    this.endTime = Date.now();
    return this;
  }

  addUser(user: string): RapidaLogBuilder {
    this.meta = {
      "Rapida-User-Id": user,
    };
    return this;
  }

  private buildMeta(): Record<string, string> {
    return {
      "Rapida-Request-Id": this.id,
      ...this.meta,
    };
  }

  build(): RapidaAsyncLogRequest {
    if (this.response === undefined) {
      throw new Error("Response is undefined");
    }

    return {
      providerRequest: {
        json: this.RequestBody,
        url: "",
        meta: this.buildMeta(),
      },
      providerResponse: {
        json: { ...this.response, model: this.RequestBody.model },
        status: 200,
        headers: {},
      },
      timing: {
        startTime: {
          seconds: Math.trunc(this.startTime / 1000),
          milliseconds: this.startTime % 1000,
        },
        endTime: {
          seconds: Math.trunc(this.endTime / 1000),
          milliseconds: this.endTime % 1000,
        },
      },
    };
  }
}

export class RapidaLogger {
  protected options: IRapidaAsyncClientOptions;
  public rapida: Rapida;
  private logger: RapidaAsyncLogger;

  constructor(options: IRapidaAsyncClientOptions) {
    this.options = options;
    this.rapida = new Rapida(options);
    this.logger = new RapidaAsyncLogger(options);
  }

  async submit(request: RapidaLogBuilder): Promise<Response> {
    const asyncLogRequest = request.build();
    return await this.logger.log(asyncLogRequest, Provider.CUSTOM_MODEL);
  }
}
