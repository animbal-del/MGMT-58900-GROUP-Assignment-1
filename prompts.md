# Group Assignment 1 — Prompt Log

MIS 58900 · Airbnb Dallas dataset

This file records, for each of the 16 questions, how we interpreted the question and the
exact prompt used to generate the code. Written before any code was generated.

---

## Dataset facts that apply to every question

Read these once; several questions are easy to get wrong without them.

- **The file is panel data, not a listing list.** `airbnb_dallas.csv` has ~48,711 rows.
  Each row is one property in one Superhost evaluation period, identified by
  `Airbnb Property ID` + `superhost_period_all`. A single property appears in many rows.
  So "average revenue for Superhosts" means an average over property-periods unless we
  deliberately collapse to one row per property first, and we should say which we did.
- **Most columns have a `prev_` twin** holding the same measure from the previous period:
  `revenue` / `prev_revenue`, `Nightly Rate` / `prev_Nightly Rate`,
  `booked_days` / `prev_booked_days`, and so on. This is what makes before/after
  comparisons possible within a single row.
- **Superhost status columns.** `Superhost` and `host_is_superhost_in_period` are 0/1 flags
  for the current period; `prev_host_is_superhost` is the prior period.
  `superhost_change_gain_superhost` = 1 on the period a property gained the badge,
  `superhost_change_lose_superhost` = 1 when it lost it. We will use `Superhost` as the
  main grouping flag and confirm it agrees with `host_is_superhost_in_period`.
- **Time columns.** `superhost_period_all` is an ordered period number.
  `Scraped Date` is a real date and is what we should use for anything seasonal.
- **Money and volume columns.** `revenue`, `occupancy_rate`, `booked_days`, `available_days`,
  `Nightly Rate`, `booked_days_avePrice`, `available_days_aveListedPrice`.
- **Rating and review columns.** `rating_ave_pastYear`, `numReviews_pastYear`,
  `num_5_star_Rev_pastYear`, `prop_5_StarReviews_pastYear`, `numCancel_pastYear`.
- **Location columns.** `Neighborhood`, `Zipcode`, `Latitude`, `Longitude`, `census_tract`.
- **Category columns.** `Listing Type` (Entire home/apt, Private room, Shared room),
  `Property Type`, `Bedrooms`, `Bathrooms`.
- **Missing values are real.** Several columns have blanks (e.g. `prev_` columns are empty
  for a property's first period). Every prompt below says to report how many rows were
  dropped rather than silently dropping them.

### Standing instructions attached to every code prompt

1. Use pandas, matplotlib and seaborn. No other plotting libraries.
2. Load the CSV once at the top of the notebook into `df`; do not reload per question.
3. Label every chart: title, axis labels with units, and a legend when there is more than
   one series.
4. Print the numbers the chart is based on, not just the picture, so we can quote figures
   in our written answer.
5. State the row count used and the number of rows dropped for missing values.
6. Keep each question's code in its own cell under a markdown heading `## Question N`.
7. End every answer with what the finding means for a business decision. Name the analysis
   type (descriptive / predictive / prescriptive) and the lever it pulls — operational
   excellence, product/service innovation, customer intimacy or value-chain coordination for
   value creation; pricing or unit economics for value capture. Questions 11, 15 and 16 ask
   for this in so many words; the rest are graded on it regardless.
8. Distinguish groups by marker shape, linestyle or hatch as well as colour. The deliverable
   is a PDF that will be read in greyscale, where a colour-only encoding disappears.

---

## Question 1 — Range and IQR of Nightly Rate

**What is being asked.** Two specific spread measures for the single column `Nightly Rate`
across the whole dataset, then an interpretation of what the gap between them means. Range
is max minus min and is driven entirely by the two most extreme listings. IQR is the 75th
percentile minus the 25th and describes the middle half. If range is enormous and IQR is
modest, that tells us a small number of very expensive listings are stretching the top end.

**Watch for.** Nightly rates of 0 or absurdly high values are likely data errors and will
dominate the range. Report them rather than deleting them quietly.

**Prompt.**
> Using the dataframe `df` from airbnb_dallas.csv, compute for the column `Nightly Rate`:
> count of non-null values, min, max, range (max − min), Q1, Q3, IQR (Q3 − Q1), and median.
> Print them as a labeled table. Also print how many rows have a null `Nightly Rate`, and
> list the 5 highest and 5 lowest nightly rates with their `Airbnb Property ID` and
> `Neighborhood` so we can judge whether the extremes are real listings or data errors.
> Do not remove outliers.

**Revision after seeing the data.** The five highest rates are the same property observed in
five periods, so "top 5 rows" is not "top 5 listings". Since the question asks about spread
"across different listings", we added a listing-level check: collapsing to one median rate per
`Airbnb Property ID` (9,599 listings, against 48,711 rows) gives range $1,899, IQR $108.10,
median $105.00 — materially the same answer. Worth one line in the write-up, because it shows
the conclusion is not an artefact of the panel structure.

---

## Question 2 — Descriptive statistics for booked_days and revenue

**What is being asked.** Mean, median, standard deviation, min and max for two columns, plus
a reading of what they say about how the properties are performing. The comparison of mean
against median is the interesting part: if mean revenue is well above median revenue, the
average is being pulled up by a minority of high earners and the median is the better
description of a typical property.

**Watch for.** `booked_days` is bounded by the length of the period, so its max is
interpretable; revenue has no upper bound.

**Prompt.**
> For the columns `booked_days` and `revenue` in `df`, produce a summary table with count,
> mean, median, standard deviation, min, and max for each. Round to two decimals and print
> as a single pandas DataFrame with the statistics as rows and the two variables as columns.
> Below the table, print the ratio of mean to median for each variable and the number of
> null values in each.

**Revision after seeing the data.** 16,861 of 48,711 property-periods (34.6%) have no booked
days, recorded as null rather than zero — so `dropna` is the right filter, but it silently
removes a third of the inventory. The question asks how the statistics describe "the overall
performance of the properties", so the full-population figures should lead and the
booked-only subset follow. Reporting only booked rows answers a narrower question than the
one asked, and the idle third is arguably the most important performance finding in it.

---

## Question 3 — Booking patterns, Superhost vs non-Superhost

**What is being asked.** Compare the distribution of `booked_days` between the two groups,
choose a visualization, and say what the difference is. The question says "determine the
best way to visualize," so we have to justify the chart choice, not just produce one.

**Our choice and why.** Side-by-side box plots, with a histogram or KDE overlay as a second
view. A bar chart of two means would hide the spread, and spread is the whole point of a
booking-pattern comparison. Box plots show median, IQR and outliers for both groups at once.

**Watch for.** The two groups are very different sizes, so we should print group counts next
to the chart and compare medians rather than only means.

**Prompt.**
> Compare `booked_days` between Superhosts (`Superhost` == 1) and non-Superhosts
> (`Superhost` == 0) in `df`. Produce: (1) a summary table with count, mean, median, std,
> Q1 and Q3 of `booked_days` for each group; (2) side-by-side box plots of `booked_days`
> by Superhost status; (3) overlapping density plots of `booked_days` for the two groups on
> one axis with a legend. Label Superhost status as "Superhost" and "Non-Superhost" rather
> than 1 and 0. Print the difference in medians and the difference in means.

---

## Question 4 — Seasonal patterns in booking days for Superhosts

**What is being asked.** Whether `booked_days` for Superhosts rises and falls with time of
year. This is the first question that needs the date column rather than the period number,
because "seasonal" means calendar months, not evaluation periods.

**Our choice and why.** A line chart of mean `booked_days` by calendar month, restricted to
Superhosts. Adding the non-Superhost line as a comparison is worth doing even though the
question doesn't ask, because a shared seasonal shape tells us it's the Dallas market rather
than something about Superhosts.

**Watch for.** `Scraped Date` needs parsing to datetime. Also check how many years the data
covers before averaging months across years, and say so.

**Prompt.**
> Parse `Scraped Date` in `df` to datetime. Print the min and max date and the number of
> distinct years. Then, for Superhosts only (`Superhost` == 1), compute mean `booked_days`
> by calendar month and plot it as a line chart with month on the x-axis. Add a second line
> for non-Superhosts on the same axes for comparison, with a legend. Print the underlying
> monthly means as a table. Also print the count of rows behind each month so we can see if
> any month is thinly sampled.

**Revision after seeing the data.** The scrape is quarterly. Only 8 of 12 calendar months
appear at all, and 4 of those hold a few dozen straggler rows against 3,000+ in the genuine
scrape months, so we read the pattern off the four well-sampled months (Feb, May, Aug, Nov)
and exclude the rest. Note also that the question's wording admits two readings — "seasonal"
points at calendar months, "over different periods" points at `superhost_period_all`. We
report both and say so, rather than picking one and hoping it was the intended one.

---

## Question 5 — Superhost status and number of reviews

**What is being asked.** Whether Superhosts get more reviews, using `numReviews_pastYear`.
"Choose an appropriate method to compare" means we pick the comparison and defend it.

**Our choice and why.** Group summary statistics plus box plots, and an independent-samples
t-test (Welch's, since group sizes and variances differ) to say whether the gap is larger
than sampling noise. Review counts are right-skewed, so we will also report the medians and
run a Mann-Whitney U as a check that doesn't assume normality.

**Watch for.** Note in the written answer that this is correlational. Superhost status is
partly awarded on the basis of review activity, so we cannot claim the badge causes reviews.

**Prompt.**
> Compare `numReviews_pastYear` between Superhosts and non-Superhosts in `df`. Produce:
> (1) a summary table with count, mean, median, std for each group; (2) side-by-side box
> plots; (3) a Welch's t-test using scipy.stats.ttest_ind with equal_var=False, printing the
> t-statistic and p-value; (4) a Mann-Whitney U test as a non-parametric check, printing the
> statistic and p-value. Print how many rows were dropped for null `numReviews_pastYear`.

**Revision after seeing the data.** This prompt did not anticipate the confound that decided
the answer. Superhosts turn out to have a *higher median* review count but a *lower mean*, and
when two statistics contradict each other a p-value cannot adjudicate between them. The cause
is that `numReviews_pastYear` scales with the size of the host's portfolio — it reflects the
host, not the property — and large commercial operators are concentrated among non-Superhosts.
Follow-up prompt used:

> Count distinct `Airbnb Property ID` values per host in `df` and print mean
> `numReviews_pastYear` by portfolio-size band. Then restrict to hosts with exactly one listing
> and re-run the Superhost / non-Superhost comparison, printing count, mean and median per
> group. Report Cohen's d alongside the p-values, since at n ≈ 37,000 almost any difference
> reaches significance and effect size is the more informative number.

---

## Question 6 — Histogram of revenue, split by Superhost status

**What is being asked.** The shape of the revenue distribution, and how that shape differs
between the two groups. The question names the chart type, so no choice to justify here.

**Watch for.** Revenue is heavily right-skewed, so a plain histogram will be one tall bar at
zero and a flat tail. We should show both a raw-scale version and a log-scale x-axis version,
and say which one we are reading the answer from. Also decide and state whether zero-revenue
rows (properties with no bookings in the period) stay in.

**Prompt.**
> Plot overlapping histograms of `revenue` in `df` for Superhosts and non-Superhosts, with
> transparency and a legend, using a shared set of bins. Produce two versions: one on the raw
> revenue scale, and one with a log-scaled x-axis. Below the charts, print for each group the
> count, mean, median, skewness of `revenue`, and the number of rows with revenue equal to 0.

---

## Question 7 — Average revenue before vs after gaining Superhost status

**What is being asked.** A bar chart comparing revenue before and after a property became a
Superhost, and whether revenue went up. This is the question that most needs the panel
structure explained above.

**How to do it correctly.** Filter to the rows where `superhost_change_gain_superhost` == 1.
Those are exactly the property-periods where the badge was gained. Within those rows,
`prev_revenue` is the before value and `revenue` is the after value for the same property.
Comparing all-Superhost revenue against all-non-Superhost revenue would answer a different
and much weaker question, because it compares different properties.

**Watch for.** Report the number of properties in this group. Also run a paired test, since
we have the same property measured twice, and report the mean of the per-property change
rather than only the difference of the two means.

**Prompt.**
> In `df`, select rows where `superhost_change_gain_superhost` == 1 — these are the periods
> in which a property gained Superhost status. Print how many rows and how many distinct
> `Airbnb Property ID` values this is. For these rows, compute mean and median of
> `prev_revenue` (before) and `revenue` (after). Plot a bar chart with two bars, "Before
> Superhost" and "After Superhost", showing the mean, with the median printed above each bar.
> Then compute the per-row change (`revenue` − `prev_revenue`), print its mean and median,
> print the percentage of properties whose revenue increased, and run a paired t-test
> (scipy.stats.ttest_rel) on the before and after values, dropping rows where either is null.

**Revision after seeing the data.** The before/after comparison on its own said revenue *fell*
after the badge was gained, which taken at face value would mean becoming a Superhost hurts
revenue. That is almost certainly an artefact: "before" and "after" are different quarters, and
Question 4 established that bookings swing seasonally. The prompt above has no control group,
so a seasonal move and a badge effect are indistinguishable in it. Follow-up prompt used:

> Build a control group of properties that did *not* gain Superhost status, measured across the
> same period transitions as the gainers. Compute the mean period-over-period revenue change for
> both groups, matched on the period mix in which gains actually occurred, and report the
> difference-in-differences. Print the row counts behind every figure.

This is the question the standing note at the foot of this file was written for: when the answer
looks strange, suspect the interpretation before the code.

---

## Question 8 — Revenue trend over evaluation periods for Superhosts

**What is being asked.** A line chart of revenue across `superhost_period_all` for
Superhosts, and a reading of whether holding the badge is associated with revenue growth.

**Our choice and why.** Plot both groups on one line chart, mean revenue by period, so the
Superhost line has something to be compared against. A single line alone can't distinguish
"Superhosts are growing" from "the whole Dallas market is growing."

**Watch for.** Use median as well as mean, given the skew found in question 6. Print the row
count per period so we can flag periods with thin data.

**Prompt.**
> Group `df` by `superhost_period_all` and `Superhost`, computing mean revenue, median
> revenue, and row count. Plot a line chart of mean revenue against `superhost_period_all`
> with one line for Superhosts and one for non-Superhosts, with a legend and axis labels.
> Produce a second version of the same chart using median revenue. Print the grouped table
> including row counts.

---

## Question 9 — Scatter plot of rating vs revenue

**What is being asked.** The relationship between `rating_ave_pastYear` and `revenue`, shown
as a scatter plot, with the correlation stated.

**Watch for.** With ~48,000 rows a raw scatter will be a solid block of ink. Use transparency
and a small marker, and add a binned mean line so the trend is visible. Ratings cluster hard
near 5, so most of the x-range will be nearly empty; note that in the answer, because a weak
correlation here may just reflect that almost every property has a high rating.

**Prompt.**
> Plot a scatter of `rating_ave_pastYear` (x) against `revenue` (y) from `df`, using
> alpha=0.1 and small markers to handle overplotting. Overlay a line showing mean revenue
> within rating bins of width 0.1. Label axes. Print the Pearson correlation and the
> Spearman correlation between the two columns, with p-values, and the number of rows used
> after dropping nulls. Also print the distribution of `rating_ave_pastYear` in deciles so we
> can see how concentrated ratings are.

**Revision after seeing the data.** The rating distribution turned out to govern the whole
answer, and the prompt above does not ask for most of what the finished cell does. Two
discoveries drove the additions. First, **range restriction**: SD 0.246 with 90.1% of rows at
4.5 or above, and within Superhosts SD 0.085 with 99.8% at 4.6+ — so a near-zero Pearson is
partly an artefact of the ratings system, not a finding about quality. That is why the concentration
table is printed *before* the scatter and why the split-by-Superhost panel was added: it
demonstrates the mechanism (less range, less correlation). Second, the relationship **bends** —
mean revenue rises to $3,345 in the 4.8–4.99 band then falls to $2,916 at exactly 5.0. A linear
coefficient cannot see that, which is why the banded table was added. Follow-up prompt used:

> Add to the Q9 cell: (1) a rating-concentration block printed before the chart — percentiles,
> SD, and the shares at >=4.5, >=4.8, ==5.0 and <4.0; (2) a table of mean revenue, median
> revenue, median `booked_days` and **median `numReviews_pastYear`** across the rating bands
> <=4.0, 4.0–4.4, 4.4–4.6, 4.6–4.8, 4.8–4.99 and 5.0 exactly; (3) a second panel splitting the
> scatter by Superhost status with a shared y-axis, distinct markers and linestyles, and group
> sizes in the legend; (4) robustness checks — Pearson on log revenue, Pearson and Spearman
> within each Superhost group, and the correlation restricted to rows with
> `numReviews_pastYear >= 10`; (5) a re-run on `revenue_z` across all rated rows so the
> never-booked periods enter as 0. Print the SD and group shares that the write-up quotes.

The median-review column is what made the answer correct rather than merely plausible: rows at
exactly 5.0 carry a median of 7 reviews against 143 and 62 in the neighbouring bands, so a
perfect score is mostly a thin-evidence score. Without that column the table reads as "five
stars reduce revenue", which is wrong.

---

## Question 10 — Listing type composition of Superhost bookings

**What is being asked.** Which `Listing Type` accounts for most Superhost bookings, with a
chart choice we justify. Note the question says "dominates bookings," so the measure should
be total `booked_days` by listing type, not a count of listings. A listing type could have
many listings but few booked nights.

**Our choice and why.** A horizontal bar chart of total booked days by listing type for
Superhosts. Pie charts are hard to read for anything past two or three slices, and we also
want to show the non-Superhost split alongside, which a pie can't do cleanly.

**Prompt.**
> For Superhosts only in `df`, compute the total `booked_days` and the number of rows for
> each `Listing Type`, plus each type's share of total Superhost booked days. Print as a
> table sorted descending. Plot a horizontal bar chart of the share of total booked days by
> listing type. Then produce the same table and chart for non-Superhosts and print the two
> shares side by side so we can compare the composition.

**Revision after seeing the data.** The plan above — a horizontal bar of booked-night shares —
was right about the *measure* and wrong about the *chart*, and it missed the finding entirely.
Three things forced a redesign. First, `Listing Type` has **four** values, not the three listed
at the top of this file: Hotel room (111 rows) exists and first appears at
`superhost_period_all` = 8, so its arrival is a source taxonomy change rather than a segment
that grew. Second, and the actual result: the answer depends on which denominator you use.
Entire home/apt is 74.5% of Superhost booked nights but **89.1% of Superhost revenue**, because
it earns $145.61 per booked night against $54.67 for a private room. Reporting nights alone
would have a manager ranking segments the revenue ledger ranks differently. Third, the
intuitive story is false: the listing *mix* is near-identical across groups (76.6% vs 75.1%
entire home), and Superhost bookings are in fact **more** tilted toward private rooms (22.1%)
than non-Superhost bookings (15.7%) — the opposite of "Superhosts favour entire homes".
Follow-up prompt used:

> Replace the single bar with a two-panel figure of 100% stacked horizontal bars sharing a
> 0–100% x-axis. Panel A: Superhost vs non-Superhost by share of booked nights. Panel B:
> Superhosts only, three bars — % of listings, % of booked nights, % of revenue — so the
> denominators can be read against each other. Give every listing type a distinct fill **and**
> hatch. Add a table of mean booked nights per on-market property-period by type x Superhost
> status to separate composition from booking intensity, a check that the shares are unchanged
> when collapsed to one row per property, and a by-period pivot to test whether the headline
> share is stable. Print the shared-room host concentration and the first period in which
> Hotel room appears.

The by-period check earned its place: the entire-home share drifts from 65.6% (period 5) to
84.2% (period 20), so the pooled 74.5% averages a moving target — the same mistake Question 8's
revision corrected.

---

## Question 11 — Correlation matrix heatmap

**What is being asked.** A heatmap of correlations among exactly four columns: `revenue`,
`occupancy_rate`, `rating_ave_pastYear`, `numReviews_pastYear`; then which pairs are
strongest and what a host should do about it.

**Watch for.** Revenue and occupancy are mechanically linked, since revenue is roughly nights
booked times price. A strong correlation there is arithmetic, not a business insight, and our
written answer should say so rather than presenting it as a finding.

**Prompt.**
> Build a correlation matrix in `df` for the columns `revenue`, `occupancy_rate`,
> `rating_ave_pastYear`, and `numReviews_pastYear`, using **listwise** complete cases — drop
> rows null on any of the four, so every cell of the matrix rests on the same rows.
> Print the matrix rounded to two decimals and print the number of rows used. Plot it as a
> seaborn heatmap with annotations, a diverging colormap centered at 0, and vmin=-1, vmax=1.
> Also print the same matrix using Spearman correlation. Finally, print a short note stating
> that `revenue` and `occupancy_rate` are mechanically linked — revenue is roughly nights
> booked times price — so a strong correlation between those two is arithmetic rather than a
> business finding, and rank the remaining pairs by strength.

**Revision after seeing the data.** The prompt above originally said *pairwise* complete
observations. That is wrong here, for a reason that only shows up once Question 9 exists:
pairwise varies the sample per cell (26,686 to 37,082 rows) and yields revenue~numReviews
Spearman 0.219 and revenue~occupancy 0.549, where Question 9 printed 0.215 and 0.544 on its
complete-case frame. The two cells would disagree inside the same PDF. Listwise keeps every
coefficient on the same 26,686 rows and matches Q9 exactly, at the cost of dropping 22,025 rows
— which are not missing at random (they are largely the listed-but-unbooked and off-market
periods from Q2/Q3), so the matrix describes listings that actually booked and were reviewed.
Say that rather than presenting it as the Dallas market as a whole.

**Note on scope.** This question has two halves and the second is easy to drop: "...and how
might these impact **business decisions for hosts**?" A heatmap plus coefficients answers only
the first. The write-up has to close on what a host should actually do differently.

---

## Question 12 — Neighborhoods with highest revenue and occupancy for Superhosts

**What is being asked.** A neighborhood-level ranking on two measures at once, for
Superhosts, with a chart choice we justify.

**Our choice and why.** Two ranked horizontal bar charts, one per measure, limited to the top
15 neighborhoods, plus a scatter of mean revenue against mean occupancy with neighborhoods as
points so we can see whether the same neighborhoods top both lists. Also apply a minimum
sample size, because a neighborhood with three listings can top a ranking on noise alone.

**Prompt.**
> For Superhosts only in `df`, group by `Neighborhood` and compute mean `revenue`, mean
> `occupancy_rate`, and row count. Drop neighborhoods with fewer than 30 rows and print how
> many were dropped and their names. Plot two horizontal bar charts: top 15 neighborhoods by
> mean revenue, and top 15 by mean occupancy rate. Then plot a scatter of mean occupancy rate
> (x) against mean revenue (y) with one point per neighborhood, labeling the top 10 by
> revenue. Print the full grouped table sorted by mean revenue.

**Revision after seeing the data.** Three parts of the plan above break on this dataset.
(1) **"Top 15 neighborhoods" assumes many categories; there are only 17**, so a top-15 is a
list, not a ranking. (2) **The "fewer than 30 rows" filter does not filter.** This is panel
data — three properties observed across thirteen periods give thirteen rows — so a row
threshold counts repeat observations of the same listing as independent evidence, and drops
only 2 of 17. We set the threshold in distinct **properties** instead (>= 20), keeping 11.
(3) **Mean revenue picks the wrong winner.** Lake Highlands leads on mean ($6,088) purely
because the top 5 of its 78 Superhost properties supply 66.6% of its revenue; its median is
$1,948, ranking 6th. Median is the headline, with the sensitivity printed so the choice is
visible.

The larger addition is a trap check the plan had no way to anticipate before Question 10
existed. Superhost revenue per booked night runs $145.61 for an entire home against $54.67 for
a private room, so a neighbourhood can top a revenue ranking on inventory mix alone — and it
does: entire-home share correlates with neighbourhood median revenue at **r = +0.822**, and
holding listing type constant moves 5 of 11 neighbourhoods by three or more rank places
(Northwest Dallas 5th -> 1st, Lakewood 3rd -> 8th). Follow-up prompt used:

> For Superhosts, keep neighbourhoods with at least 20 distinct `Airbnb Property ID` values.
> Report median as the headline with mean alongside and a trimmed-mean sensitivity check.
> Produce two ranked horizontal bar panels — median revenue, then median occupancy **in the
> revenue panel's category order, not re-sorted** — plus a scatter of median realised nightly
> rate against median occupancy with quadrant lines at the city-wide Superhost medians. Then
> test whether the revenue ranking is a listing-type artefact: correlate entire-home share with
> median revenue, and re-rank within `Listing Type == "Entire home/apt"` only, printing the
> rank shift. Also re-rank on the on-market frame with idle periods as $0 to show whether the
> ranking is robust to frame choice.

**One result worth recording, because it contradicts Question 11.** Within properties, Q11
found realised nightly price *falls* as occupancy rises. Across neighbourhoods the sign
reverses: Spearman(median occupancy, median realised rate) = **+0.600** — busier districts are
generally pricier. There is no neighbourhood-level plateau, and the notebook says so
explicitly. The underpricing story survives only as a three-neighbourhood quadrant exception
(Lakewood, Northwest Dallas, Forest Hills/Casa Linda). A relationship that holds at one level
of aggregation does not transfer to another; Question 16 needs care on exactly this point.

---

## Question 13 — Superhost status and pricing strategy

**What is being asked.** Whether Superhosts price differently, using `Nightly Rate`, with a
chart type we choose.

**Our choice and why.** Violin plots by Superhost status, because they show the full shape of
the price distribution rather than just five summary numbers, and pricing strategy is about
where hosts cluster. We will also break it out by `Listing Type`, since an entire home and a
private room are not competing on the same price, and an overall comparison could be entirely
a composition effect.

**Prompt.**
> Compare `Nightly Rate` between Superhosts and non-Superhosts in `df`. Produce: (1) a
> summary table with count, mean, median, std, Q1, Q3 by group; (2) violin plots of
> `Nightly Rate` by Superhost status, with the y-axis capped at the 99th percentile so the
> shape is readable; (3) the same comparison faceted by `Listing Type`, with a grouped bar
> chart of median nightly rate by listing type and Superhost status. Print the median
> difference overall and within each listing type.

---

## Question 14 — Five-star reviews and revenue

**What is being asked.** What `num_5_star_Rev_pastYear` says about revenue generation, with a
visualization we choose.

**Our choice and why.** A binned scatter or box plot of revenue across bands of five-star
review counts, rather than a raw scatter, because the count variable is discrete and highly
skewed. We should also look at `prop_5_StarReviews_pastYear`, the proportion, since a property
with 100 reviews and 60 five-star ones is a different story from one with 60 reviews all
five-star, and the raw count partly just measures how long a property has been booked.

**Prompt.**
> Examine the relationship between `num_5_star_Rev_pastYear` and `revenue` in `df`. Produce:
> (1) a scatter with alpha=0.1 plus a binned mean line; (2) box plots of `revenue` across
> quintile bands of `num_5_star_Rev_pastYear`, with the band ranges printed; (3) the Pearson
> and Spearman correlations for both `num_5_star_Rev_pastYear` vs `revenue` and
> `prop_5_StarReviews_pastYear` vs `revenue`, so we can separate volume of five-star reviews
> from the proportion of them. Print row counts used.

---

## Question 15 — Story of place

**What is being asked.** An open-ended narrative question about location, backed by
neighborhood-level or map evidence, framed as something you would present to Airbnb
management. This one is graded on the story, so the code just needs to produce the evidence.

**Our approach.** A scatter map of listings using `Latitude` and `Longitude`, colored by
nightly rate, plus a neighborhood table combining median price, median occupancy, median
revenue, and listing count. The story we are looking for is whether high price and high
occupancy occur in the same places, since a neighborhood with high prices and low occupancy
is a different management problem from one with both high.

**Watch for.** No internet-dependent map tiles, since the notebook has to run in Colab and
export cleanly to PDF. A plain latitude/longitude scatter is enough.

**Prompt.**
> Using `Latitude` and `Longitude` in `df`, plot a scatter map of listings with points
> colored by `Nightly Rate` (capped at the 95th percentile for the color scale) and a
> colorbar, with equal aspect ratio and no external map tiles. Produce a second version
> colored by `occupancy_rate`. Then build a neighborhood table with listing count, median
> nightly rate, median occupancy rate, median revenue, and Superhost share, filtered to
> neighborhoods with at least 30 rows, sorted by median revenue. Print the top 15 and bottom
> 15 rows of that table.

---

## Question 16 — Recommendation to Airbnb management

**What is being asked.** One concrete proposed change, a KPI that justifies it, evidence from
our own earlier analysis, and the trade-offs. This is a writing question, not a coding one.
The only code needed is whatever specific number we end up quoting.

**Our approach.** Pick the recommendation after seeing questions 1 through 15, so the evidence
is real rather than reverse-engineered. Write it as: the change, the KPI it moves, the two or
three figures from our analysis that support it, and at least one honest cost of making the
change.

**Prompt (to be filled in once the analysis is done).**
> Based on the following findings from our analysis [paste the specific numbers], write the
> supporting calculation for the recommendation that [state the change]. Compute [the
> specific figure] and print it with the row counts behind it. Do not invent numbers; use only
> the columns in `df`.

---

## Notes for the group

- Everything above is our interpretation before running any code. If a question's answer
  looks strange when we run it, check this file first — the interpretation may be what is
  wrong, not the code.
- Where the data contradicted an assumption, we left the original prompt in place and added a
  **"Revision after seeing the data"** block beneath it with the follow-up prompt actually
  used. Questions 1, 2, 4, 5, 7, 9, 10, 11 and 12 have one. The revisions are the point, not an admission —
  the spec changing when the evidence demanded it is the process this assignment is asking us
  to show.
- Question 7 is the one most likely to be done incorrectly by a quick prompt. Make sure the
  before/after comparison uses `superhost_change_gain_superhost` and the `prev_` columns.
- Questions 3, 4, 5, 10, 12, 13, 14 and 15 all say "choose the best way to visualize."
  Each of our answers needs a sentence saying why we picked that chart, not just the chart.
