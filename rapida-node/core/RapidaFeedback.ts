import { IRapidaMeta } from "./RapidaClientOptions";
import { fetch, Response } from "@whatwg-node/fetch";

export enum RapidaFeedbackRating {
  Positive = "positive",
  Negative = "negative",
}

export class RapidaFeedback {
  static async logFeedback(
    rapidaMeta: IRapidaMeta,
    rapidaId: string,
    rating: boolean
  ): Promise<void> {
    const options = {
      method: "POST",
      headers: {
        "Rapida-Auth": `Bearer ${rapidaMeta.apiKey}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        "rapida-id": rapidaId,
        rating: rating,
      }),
    };

    let response: Response;
    let url: URL;
    try {
      url = new URL(rapidaMeta.baseUrl);
      url.pathname = "/v1/feedback";
      response = await fetch(url, options);
    } catch (error: any) {
      console.error(
        "Error making request to Rapida feedback endpoint:",
        error
      );
      return;
    }

    if (!response.ok) {
      console.error("Error logging feedback: ", response.statusText);
    }

    const responseBody = await response.text();
    const consumerResponse = new Response(responseBody, response);
    if (rapidaMeta.onFeedback) {
      await rapidaMeta.onFeedback(consumerResponse);
    }
  }
}
