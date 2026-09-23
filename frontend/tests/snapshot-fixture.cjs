// Synthetic contract fixture; never used as research evidence or publication data.
const CORE = ["copy", "overview", "gpr_timeline", "evidence_map", "event_study", "regression", "reader_summaries", "country_coverage"];

function validSnapshot(extraDatasets = []) {
  const headline = { country_count: 1, shock_count: 0, selected_event_count: 0, represented_event_count: null, start_date: "2024-01-01", end_date: "2024-01-03" };
  const inference = { std_error: 0.001, t_stat: 0, p_value: 1, observation_count: 2, event_count: 1, accumulation_start_day: -1 };
  const coefficient = (term) => ({ term, estimate: 0, std_error: null, t_stat: null, p_value: null });
  return {
    manifest: { available: true, schema_version: 1, profile: "public", datasets: [...CORE, ...extraDatasets], build_date: "2024-01-04", ...headline },
    copy: {
      central_question: "Test question", intro: "Synthetic fixture", main_takeaway: "Test result", use_note: "Not empirical evidence",
      job_statements: [{ title: "Question", body: "Description" }], reader_path: [{ step: "1", title: "Read", body: "Description" }],
      current_answer_points: ["Test answer"], does_not_prove_points: ["Test limitation"],
      method_map: [{ Question: "Test", Tool: "Regression", Output: "Coefficients", "What to look for": "Uncertainty" }],
      glossary: { risk: "Test definition" }, how_to_read: { market_response: "Read the response", regression: "Read the estimate" },
    },
    overview: { headline, definitions: {
      shock_days: "Persisted GPR-change flags within displayed coverage.", largest_jumps: "Largest GPR jumps within displayed coverage.",
      selected_events: "Peak events selected using the existing Python rule; participation is unknown without saved windows.",
      event_alignment: "Day 0 is the first ETF trading observation on or after the event date.",
      accumulation: "Each ETF-event path accumulates from its first available relative day, including negative days, without resetting at day 0.",
      inference: "Not adjusted for dependence between ETFs exposed to common events. No confidence intervals are supplied.",
      return_units: "Cumulative log-return units; multiply by 100 for percent or 10,000 for basis points.",
    } },
    gpr_timeline: { series: [{ date: "2024-01-01", gpr: 0 }, { date: "2024-01-02", gpr: null }, { date: "2024-01-03", gpr: 1 }].map((row) => ({ ...row, gpr_change_shock: false, selected_for_event_study: false })), top_shocks: [], selected_events: [] },
    evidence_map: [{ Method: "Regression", "Question answered": "Test", Direction: "Uncertain", Estimate: "0 bps", "p-value / metric": "n/a", "Evidence strength": "Unavailable", "Plain-English takeaway": "Test fixture" }],
    event_study: ["developed", "emerging"].flatMap((market_group) => [
      { market_group, relative_day: 0, average_abnormal_return: 0, cumulative_average_abnormal_return: 0, cumulative_average_return: 0, ...inference },
      { market_group, relative_day: 1, average_abnormal_return: null, cumulative_average_abnormal_return: null, cumulative_average_return: null, ...inference, std_error: null, t_stat: null, p_value: null },
    ]),
    regression: {
      baseline: [coefficient("gpr_change_z"), coefficient("gpr_change_z:emerging_market")],
      controlled: [coefficient("gpr_change_z"), coefficient("gpr_change_z:emerging_market")],
      date_fe: [coefficient("gpr_change_z:emerging_market")],
    },
    reader_summaries: {
      output_files: [{ file: "event.csv", reader_page: "Market response", rows: 4, plain_meaning: "Test observations" }],
      market_reaction: [{ market_group: "Developed markets", relative_day: 0, cumulative_average_abnormal_return: 0, direction: "Uncertain", evidence_strength: "Test", plain_note: "Synthetic", ...inference }],
      regression_translation: [{ test: "Controlled association", what_it_checks: "Test", direction: "Uncertain", estimate: 0, p_value: null, evidence_strength: "Test", plain_note: "Synthetic" }],
    },
    country_coverage: [{ country: "Test country", ticker: "TEST", market_group: "developed", first_date: "2024-01-01", last_date: "2024-01-03", observation_count: 3 }],
  };
}

module.exports = { CORE, validSnapshot };
