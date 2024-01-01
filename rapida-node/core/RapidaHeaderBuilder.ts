import { IRapidaMeta } from "./RapidaClientOptions";

export class RapidaHeaderBuilder {
  private rapidaMeta: IRapidaMeta;
  private headers: { [key: string]: string } = {};

  constructor(rapidaMeta: IRapidaMeta) {
    this.rapidaMeta = rapidaMeta;
    const apiKey = rapidaMeta?.apiKey ?? process.env.HELICONE_API_KEY;
    this.headers = {
      "Rapida-Auth": `Bearer ${apiKey}`,
    };
  }

  withPropertiesHeader(): RapidaHeaderBuilder {
    if (!this.rapidaMeta?.properties) return this;
    this.headers = {
      ...this.headers,
      ...this.getPropertyHeaders(this.rapidaMeta.properties),
    };
    return this;
  }

  withCacheHeader(): RapidaHeaderBuilder {
    if (!this.rapidaMeta?.cache) return this;
    this.headers = {
      ...this.headers,
      ...this.getCacheHeaders(this.rapidaMeta.cache),
    };
    return this;
  }

  withRetryHeader(): RapidaHeaderBuilder {
    if (!this.rapidaMeta?.retry) return this;
    this.headers = {
      ...this.headers,
      ...this.getRetryHeaders(this.rapidaMeta.retry),
    };
    return this;
  }

  withRateLimitPolicyHeader(): RapidaHeaderBuilder {
    if (!this.rapidaMeta?.rateLimitPolicy) return this;
    this.headers = {
      ...this.headers,
      ...this.getRateLimitPolicyHeaders(this.rapidaMeta.rateLimitPolicy),
    };
    return this;
  }

  withUserHeader(): RapidaHeaderBuilder {
    if (!this.rapidaMeta?.user) return this;
    this.headers = {
      ...this.headers,
      ...this.getUserHeader(this.rapidaMeta.user),
    };
    return this;
  }

  build(): { [key: string]: string } {
    return this.headers;
  }

  private getUserHeader(user?: string): { [key: string]: string } {
    return user ? { "Rapida-User-Id": user } : {};
  }

  private getPropertyHeaders(properties?: { [key: string]: any }): {
    [key: string]: string;
  } {
    if (!properties) return {};
    const headers: { [key: string]: string } = {};
    for (const key in properties) {
      headers[`Rapida-Property-${key}`] = properties[key].toString();
    }
    return headers;
  }

  private getCacheHeaders(cache?: boolean): { [key: string]: string } {
    return cache ? { "Rapida-Cache-Enabled": "true" } : {};
  }

  private getRetryHeaders(retry?: boolean | { [key: string]: any }): {
    [key: string]: string;
  } {
    if (!retry) return {};
    const headers: { [key: string]: string } = {
      "Rapida-Retry-Enabled": "true",
    };
    if (typeof retry === "object") {
      if (retry.num) headers["Rapida-Retry-Num"] = retry.num.toString();
      if (retry.factor)
        headers["Rapida-Retry-Factor"] = retry.factor.toString();
      if (retry.min_timeout)
        headers["Rapida-Retry-Min-Timeout"] = retry.min_timeout.toString();
      if (retry.max_timeout)
        headers["Rapida-Retry-Max-Timeout"] = retry.max_timeout.toString();
    }
    return headers;
  }

  private getRateLimitPolicyHeaders(
    rateLimitPolicy?: string | { [key: string]: any }
  ): { [key: string]: string } {
    if (!rateLimitPolicy) return {};
    let policy = "";
    if (typeof rateLimitPolicy === "string") {
      policy = rateLimitPolicy;
    } else if (typeof rateLimitPolicy === "object") {
      policy = `${rateLimitPolicy.quota};w=${rateLimitPolicy.time_window}`;
      if (rateLimitPolicy.segment) policy += `;s=${rateLimitPolicy.segment}`;
    } else {
      throw new TypeError(
        "rate_limit_policy must be either a string or a dictionary"
      );
    }
    return { "Rapida-RateLimit-Policy": policy };
  }
}
