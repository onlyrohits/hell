import { IRapidaMeta } from "./RapidaClientOptions";
import { RapidaFeedback, RapidaFeedbackRating } from "./RapidaFeedback";

export class Rapida {
  public rapidaIdHeader = "rapida-id";

  constructor(private rapidaMeta: IRapidaMeta) {}

  public async logFeedback(rapidaId: string, rating: RapidaFeedbackRating) {
    const ratingAsBool = rating === RapidaFeedbackRating.Positive;

    await RapidaFeedback.logFeedback(
      this.rapidaMeta,
      rapidaId,
      ratingAsBool
    );
  }
}
