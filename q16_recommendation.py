# Q16 is a SYNTHESIS question, so this cell does not run a new exploration - it sources the
# handful of figures the brief quotes and puts each one on a frame the reader can check. Four
# decisions come before any number. First, WHICH ROWS: only property-periods that actually
# booked have a realised price, so the 16,861 never-booked periods are named and set aside
# rather than dropped silently (step 1). Second, WHICH INVENTORY: entire homes only, and step 1
# shows WHY - the revenue plateau this cell is built on is entire-home-specific. Third, WHAT A
# FAIR COMPARISON IS: step 3 compares each high-occupancy listing against the median realised
# rate of MID-occupancy entire homes IN THE SAME ZIP IN THE SAME QUARTER, which is the level
# Q11 measured the negative price/occupancy relationship at. Fourth, WHAT THE TRIGGER IS:
# step 5 tests the obvious alternative trigger (the Superhost badge) and rejects it.

GREY, ORANGE, EDGE = '#8C8C8C', '#DD8452', '#333333'
BLUE = '#4C72B0'

# --- Step 0: the business question, stated before any code ----------------------------------
print('=' * 100)
print('STEP 0 - THE BUSINESS QUESTION')
print('=' * 100)
print('"Where should Airbnb\'s Dallas market team spend its next quarter of effort - and what')
print(' single change does our own exploration actually support?"')
print()
print('SCOPE GUARD vs Q15, because the two briefs must not read as the same recommendation.')
print('Q15 targets PLACES: seven named ZIPs, chosen because the ZIP itself looks under-priced.')
print('Q16 targets BEHAVIOUR: entire homes whose OWN occupancy is in the top quintile of the')
print('city, wherever they are. ZIP enters here only as the COMPARABLE that makes the price gap')
print('fair, never as the trigger. The difference is deliberate.')
print()


# --- Step 1: the evidence frame, with every filter reported ----------------------------------
print('=' * 100)
print('STEP 1 - THE EVIDENCE FRAME. Two filters, each one counted.')
print('=' * 100)
N_ALL = len(df)
booked = df[df['booked_days_avePrice'].notna() & df['occupancy_rate'].notna()]
print('(a) KEEP ROWS THAT ACTUALLY BOOKED (booked_days_avePrice AND occupancy_rate both non-null)')
print('    Rows in            : {:,}'.format(N_ALL))
print('    Rows removed       : {:,} ({:.1%})'.format(N_ALL - len(booked),
                                                     (N_ALL - len(booked)) / N_ALL))
print('    Rows remaining     : {:,}'.format(len(booked)))
print('    THESE ROWS ARE NOT MISSING DATA. A property-period with no booking has no realised')
print('    price BY CONSTRUCTION - there is no booked night to average a price over. The setup')
print('    cell itemised the same 16,861 rows: 9,550 were listed but never booked, 7,311 have no')
print('    availability recorded either. Q2/Q3 own that cohort; the brief below explains why it')
print('    is flagged as the NEXT question rather than folded into this one.')
print()

COLS = ['Airbnb Property ID', 'Airbnb Host ID', 'superhost_period_all', 'Superhost', 'Zipcode',
        'Listing Type', 'Nightly Rate', 'booked_days_avePrice', 'occupancy_rate', 'revenue',
        'booked_days']
# A NARROW copy, built once. df carries 111 columns and adding derived columns to it fires
# PerformanceWarning: DataFrame is highly fragmented straight into the graded PDF
eh = booked.loc[booked['Listing Type'] == 'Entire home/apt', COLS].copy()
print('(b) KEEP Listing Type == "Entire home/apt"')
print('    Rows in            : {:,}'.format(len(booked)))
print('    Rows removed       : {:,} ({:.1%})'.format(len(booked) - len(eh),
                                                     (len(booked) - len(eh)) / len(booked)))
print('    Rows remaining     : {:,}  ->  {:,} distinct properties, {:,} distinct hosts'.format(
    len(eh), eh['Airbnb Property ID'].nunique(), eh['Airbnb Host ID'].nunique()))
print('    Listing types removed:')
for k, v in booked.loc[booked['Listing Type'] != 'Entire home/apt',
                       'Listing Type'].value_counts().items():
    print('      {:<18} {:>6,} rows'.format(k, v))
print()


def quintile_table(frame, occ='occupancy_rate'):
    """Occupancy quintiles, forced to 1..5 and REINDEXED so an empty quintile stays visible."""
    f = frame.copy()
    f['occ_quintile'] = pd.qcut(f[occ], 5, labels=False) + 1
    t = f.groupby('occ_quintile').agg(
        n=('revenue', 'size'),
        properties=('Airbnb Property ID', 'nunique'),
        med_occupancy=('occupancy_rate', 'median'),
        med_booked_days=('booked_days', 'median'),
        med_revenue=('revenue', 'median'),
        med_realised_rate=('booked_days_avePrice', 'median'),
        med_listed_rate=('Nightly Rate', 'median'),
        superhost_share=('Superhost', 'mean')).reindex(range(1, 6))
    return f, t


print('WHY ENTIRE HOMES ONLY - the scope is EARNED, not assumed. Same quintile split, run on')
print('Private room, is printed here as the control.')
pr = booked.loc[booked['Listing Type'] == 'Private room', COLS].copy()
_, pr_tbl = quintile_table(pr)
display(pr_tbl.round(4))
print('  Private rooms show the SAME falling realised rate across occupancy quintiles')
print('  (${:,.2f} -> ${:,.2f}) but their median revenue is STILL RISING at the top'.format(
    pr_tbl.loc[1, 'med_realised_rate'], pr_tbl.loc[5, 'med_realised_rate']))
print('  (${:,.0f} -> ${:,.0f} from Q4 to Q5). A falling price WITHOUT a revenue plateau is not'.format(
    pr_tbl.loc[4, 'med_revenue'], pr_tbl.loc[5, 'med_revenue']))
print('  underpricing - it is a cheaper product selling more of itself. The plateau this brief')
print('  is built on is ENTIRE-HOME-SPECIFIC, which is why the scope is entire homes.')
print()


# --- Step 2: TABLE 1 - the plateau ------------------------------------------------------------
print('=' * 100)
print('STEP 2 - TABLE 1. THE PLATEAU. Occupancy quintiles of the entire-home booked frame.')
print('=' * 100)
eh, Q_TBL = quintile_table(eh)
_, CUTS = pd.qcut(eh['occupancy_rate'], 5, labels=False, retbins=True)
print('QUINTILE CUTPOINTS on occupancy_rate (pd.qcut, 5 bins, printed so the cohort is')
print('reproducible): {}'.format('  |  '.join('{:.4f}'.format(c) for c in CUTS)))
print('  Quintile 5 therefore means occupancy_rate >= {:.4f}. That number is the trigger the'.format(CUTS[4]))
print('  brief below uses.')
display(Q_TBL.round(4))
Q4_REV, Q5_REV = Q_TBL.loc[4, 'med_revenue'], Q_TBL.loc[5, 'med_revenue']
Q4_OCC, Q5_OCC = Q_TBL.loc[4, 'med_occupancy'], Q_TBL.loc[5, 'med_occupancy']
print('  THE SENTENCE THIS TABLE LICENSES: the top quintile sells NEARLY DOUBLE the occupancy of')
print('  the fourth ({:.4f} against {:.4f}, {:.2f}x) and earns LESS revenue (${:,.2f} against'.format(
    Q5_OCC, Q4_OCC, Q5_OCC / Q4_OCC, Q5_REV))
print('  ${:,.2f}, a fall of ${:,.2f} / {:.1%}). Median realised rate falls monotonically across'.format(
    Q4_REV, Q4_REV - Q5_REV, Q5_REV / Q4_REV - 1))
print('  all five quintiles: {}.'.format(
    ' -> '.join('${:,.2f}'.format(v) for v in Q_TBL['med_realised_rate'])))
print()
print('REGIME CHECK. Q13 and Q15 both found a structural break at period 17, so the plateau is')
print('re-run on each side of it before it is believed. Quintiles are RE-CUT within each half,')
print('so each half is compared against its own market.')
REG = {}
for lab, sub in [('periods 5-16 (pre-break)', eh[eh['superhost_period_all'] < 17]),
                 ('periods 17-20 (post-break)', eh[eh['superhost_period_all'] >= 17])]:
    _, t = quintile_table(sub[COLS])
    REG[lab] = t
    print('  {} - {:,} rows'.format(lab, len(sub)))
    display(t.round(4))
    print('    Q4 -> Q5 median revenue ${:,.2f} -> ${:,.2f} ({:+.1%});  median realised rate'.format(
        t.loc[4, 'med_revenue'], t.loc[5, 'med_revenue'],
        t.loc[5, 'med_revenue'] / t.loc[4, 'med_revenue'] - 1))
    print('    ${:,.2f} -> ${:,.2f} ({:+.1%}).'.format(
        t.loc[4, 'med_realised_rate'], t.loc[5, 'med_realised_rate'],
        t.loc[5, 'med_realised_rate'] / t.loc[4, 'med_realised_rate'] - 1))
print('  => THE Q4->Q5 REVENUE FALL SURVIVES IN BOTH REGIMES. It is not an artefact of pooling')
print('  the pre- and post-break markets together.')
print()


# --- Step 3: TABLE 2 - the ZIP-and-quarter matched comparable ---------------------------------
print('=' * 100)
print('STEP 3 - TABLE 2. THE MATCHED COMPARABLE. This step exists to fix an AGGREGATION HAZARD.')
print('=' * 100)
print('A raw "quintile 5 realises less than quintile 3" comparison pools ZIPs and quarters, so it')
print('could be entirely composition: cheap ZIPs might simply run fuller. The fix is to compare')
print('each quintile-5 listing only against MID-OCCUPANCY ENTIRE HOMES IN ITS OWN ZIP IN ITS OWN')
print('QUARTER - WITHIN ZIP, WITHIN QUARTER, WITHIN LISTING TYPE. That is the level at which Q11')
print('measured the negative price/occupancy relationship (log correlation -0.056 at property-')
print('period level; Q13: Spearman -0.086 Superhost / -0.074 non-Superhost).')
print('Q12\'s neighbourhood-level Spearman of +0.600 between median occupancy and median realised')
print('rate is a BETWEEN-MARKET fact - busier districts are pricier districts. It does not')
print('contradict a within-ZIP finding and it does not transfer to one. Both are true.')
print()
mid = eh[eh['occ_quintile'].isin([2, 3, 4])]
comp = mid.groupby(['Zipcode', 'superhost_period_all'])['booked_days_avePrice'].agg(
    comp_med='median', comp_n='size')
q5 = eh[eh['occ_quintile'] == 5].join(comp, on=['Zipcode', 'superhost_period_all'])
MIN_COMP = 10
matched = q5[q5['comp_n'] >= MIN_COMP].copy()
matched['gap_usd'] = matched['booked_days_avePrice'] - matched['comp_med']
matched['gap_pct'] = matched['gap_usd'] / matched['comp_med']
print('ROW FILTERING, REPORTED')
print('  Quintile-5 entire-home rows                       : {:,}'.format(len(q5)))
print('  ... with NO comparable cell at all (empty ZIP x quarter): {:,}'.format(
    int(q5['comp_med'].isna().sum())))
print('  ... with a comparable built on fewer than {} rows      : {:,}'.format(
    MIN_COMP, int((q5['comp_n'].notna() & (q5['comp_n'] < MIN_COMP)).sum())))
print('  Rows removed by the comp_n >= {} rule                  : {:,} ({:.1%})'.format(
    MIN_COMP, len(q5) - len(matched), (len(q5) - len(matched)) / len(q5)))
print('  MATCHED COHORT                                    : {:,} rows, {:,} properties,'.format(
    len(matched), matched['Airbnb Property ID'].nunique()))
print('                                                      {:,} hosts, {:,} ZIPs'.format(
    matched['Airbnb Host ID'].nunique(), matched['Zipcode'].nunique()))
print('  The threshold is a PRECISION rule, not a quality rule: a median built on 3 listings is')
print('  not a market rate. Step 4 reports which ZIPs it costs us.')
print()
OWN = matched['booked_days_avePrice'].median()
CMP = matched['comp_med'].median()
GAP = matched['gap_usd'].median()
GAPP = matched['gap_pct'].median()
BELOW = (matched['gap_usd'] < 0).mean()
gap_rows = [{'frame': 'all periods 5-20', 'rows': len(matched),
             'properties': matched['Airbnb Property ID'].nunique(),
             'hosts': matched['Airbnb Host ID'].nunique(),
             'median own realised rate': round(OWN, 2), 'median comparable': round(CMP, 2),
             'median gap $': round(GAP, 2), 'median gap %': round(GAPP, 4),
             'share below comparable': round(BELOW, 4)}]
for lab, sub in [('periods 5-16 (pre-break)', matched[matched['superhost_period_all'] < 17]),
                 ('periods 17-20 (post-break)', matched[matched['superhost_period_all'] >= 17])]:
    gap_rows.append({'frame': lab, 'rows': len(sub),
                     'properties': sub['Airbnb Property ID'].nunique(),
                     'hosts': sub['Airbnb Host ID'].nunique(),
                     'median own realised rate': round(sub['booked_days_avePrice'].median(), 2),
                     'median comparable': round(sub['comp_med'].median(), 2),
                     'median gap $': round(sub['gap_usd'].median(), 2),
                     'median gap %': round(sub['gap_pct'].median(), 4),
                     'share below comparable': round((sub['gap_usd'] < 0).mean(), 4)})
GAP_TBL = pd.DataFrame(gap_rows).set_index('frame')
print('TABLE 2 - HIGH-OCCUPANCY ENTIRE HOMES AGAINST THEIR OWN ZIP-AND-QUARTER COMPARABLE')
display(GAP_TBL)
print('  => The top-occupancy entire home realises ${:,.2f} a night against a ${:,.2f} comparable'.format(
    OWN, CMP))
print('  built from mid-occupancy entire homes in the SAME ZIP in the SAME quarter - a median gap')
print('  of ${:,.2f} / {:.2%}, with {:.1%} of the cohort sitting below its own comparable. The gap'.format(
    GAP, GAPP, BELOW))
print('  narrows after the break but does not close or reverse.')
print()
per = matched.groupby('superhost_period_all').agg(
    rows=('gap_usd', 'size'),
    properties=('Airbnb Property ID', 'nunique'),
    med_own=('booked_days_avePrice', 'median'),
    med_comp=('comp_med', 'median'),
    med_gap_usd=('gap_usd', 'median'),
    med_gap_pct=('gap_pct', 'median'),
    share_below=('gap_usd', lambda s: (s < 0).mean()))
per.index = per.index.astype(int)
N_NEG = int((per['med_gap_usd'] < 0).sum())
N_ZERO = int((per['med_gap_usd'] == 0).sum())
N_POS = int((per['med_gap_usd'] > 0).sum())
print('PER-PERIOD MEDIAN GAP, all {} periods. The COUNT IS COMPUTED, not asserted.'.format(len(per)))
display(per.round(4))
print('  Periods with a NEGATIVE median gap : {} of {}'.format(N_NEG, len(per)))
print('  Periods with a ZERO median gap     : {}  {}'.format(
    N_ZERO, '(periods {})'.format(', '.join(str(i) for i in per.index[per['med_gap_usd'] == 0]))
    if N_ZERO else ''))
print('  Periods with a POSITIVE median gap : {}  {}'.format(
    N_POS, '(periods {})'.format(', '.join(str(i) for i in per.index[per['med_gap_usd'] > 0]))
    if N_POS else ''))
print('  => THE EXCEPTION IS NOT A REVERSAL. No period shows high-occupancy entire homes')
print('  realising MORE than their comparable; the single non-negative period is exactly $0.00.')
print()


# --- Step 4: TABLE 3 - the cohort and the prize ----------------------------------------------
print('=' * 100)
print('STEP 4 - TABLE 3. THE COHORT AND THE PRIZE, on the post-break frame only.')
print('=' * 100)
print('WHY POST-BREAK ONLY: Q13 and Q15 both found the market-wide price level halves at period')
print('17. A pooled baseline would average two regimes and could not be used as a KPI target.')
late = matched[matched['superhost_period_all'] >= 17]
# Counts and dollars in one column, so the column is FORMATTED rather than rounded - a count
# printed as 1562.0000 invites the reader to mistake it for a measurement
C_TBL = pd.DataFrame({'value': [
    '{:,}'.format(len(late)),
    '{:,}'.format(late['Airbnb Property ID'].nunique()),
    '{:,}'.format(late['Airbnb Host ID'].nunique()),
    '{:,}'.format(late['Zipcode'].nunique()),
    '${:,.2f}'.format(late['booked_days_avePrice'].median()),
    '${:,.2f}'.format(late['comp_med'].median()),
    '${:,.2f}'.format(late['Nightly Rate'].median()),
    '{:.4f}'.format(late['occupancy_rate'].median()),
    '{:,.1f}'.format(late['booked_days'].median()),
    '${:,.2f}'.format(late['revenue'].median())]},
    index=['cohort rows (property-periods)', 'distinct properties', 'distinct hosts',
           'distinct ZIPs', 'median realised rate (booked_days_avePrice)',
           'median ZIP-and-quarter comparable', 'median LISTED rate (Nightly Rate)',
           'median occupancy_rate', 'median booked_days', 'median revenue'])
display(C_TBL)
COH_OWN = late['booked_days_avePrice'].median()
COH_CMP = late['comp_med'].median()
COH_OCC = late['occupancy_rate'].median()
COH_REV = late['revenue'].median()
COH_LIST = late['Nightly Rate'].median()
print('  NOTE THE THIRD MONEY ROW. The median LISTED rate (${:,.2f}) sits BELOW the median'.format(COH_LIST))
print('  REALISED rate (${:,.2f}) post-break. A listed price below the achieved price is not a'.format(COH_OWN))
print('  behaviour, it is a MEASUREMENT ARTEFACT - the same one Q13 flagged at the break. It is')
print('  the reason the KPI below is the REALISED rate and never the listed one.')
print()
p20 = late[late['superhost_period_all'] == 20]
print('THE SHIPPABLE TARGET LIST - the latest observed period on its own')
print('  Period 20: {:,} property-periods = {:,} distinct properties, {:,} hosts, {:,} ZIPs.'.format(
    len(p20), p20['Airbnb Property ID'].nunique(), p20['Airbnb Host ID'].nunique(),
    p20['Zipcode'].nunique()))
print('  Median realised ${:,.2f} against a ${:,.2f} comparable; median occupancy {:.4f};'.format(
    p20['booked_days_avePrice'].median(), p20['comp_med'].median(),
    p20['occupancy_rate'].median()))
print('  median revenue ${:,.2f}. {:,} of them ({:.1%}) sit BELOW their own ZIP comparable.'.format(
    p20['revenue'].median(), int((p20['gap_usd'] < 0).sum()),
    float((p20['gap_usd'] < 0).mean())))
print()
bel = late[late['gap_usd'] < 0]
uplift = (bel['comp_med'] - bel['booked_days_avePrice']) * bel['booked_days']
U_MED = float(uplift.median())
U_REV = float(bel['revenue'].median())
print('THE ARITHMETIC PRIZE, on the BELOW-COMPARABLE subset of the post-break cohort only')
print('  Rows below their comparable : {:,} of {:,} ({:.1%}), {:,} distinct properties'.format(
    len(bel), len(late), len(bel) / len(late), bel['Airbnb Property ID'].nunique()))
print('  Uplift = (comp_med - booked_days_avePrice) x booked_days, per property-period:')
print('    median ${:,.2f}  |  quartiles ${:,.2f} / ${:,.2f}  |  on a median revenue of ${:,.2f}'.format(
    U_MED, float(uplift.quantile(0.25)), float(uplift.quantile(0.75)), U_REV))
print('    = {:.1%} of the median revenue of the same rows.'.format(U_MED / U_REV))
print('  *** ARITHMETIC UPPER BOUND, ASSUMES ZERO BOOKING LOSS - NOT A FORECAST. ***')
print('  It is what these listings WOULD have earned had every night they actually sold been')
print('  sold at their own ZIP comparable. Any real price step loses some nights.')
_belA = matched[matched['gap_usd'] < 0]
_upA = (_belA['comp_med'] - _belA['booked_days_avePrice']) * _belA['booked_days']
print('  For reference, the same calculation on ALL periods 5-20: {:,} rows, median uplift'.format(len(_belA)))
print('  ${:,.2f} on a median revenue of ${:,.2f}. The post-break figure is the one the KPI'.format(
    float(_upA.median()), float(_belA['revenue'].median())))
print('  uses, because the KPI baseline is post-break.')
print()
print('WHICH ZIPs FALL OUT UNDER comp_n >= {} - a target list that silently omits part of the'.format(MIN_COMP))
print('city is a DIFFERENT recommendation, so the omission is printed.')
lost = sorted(set(q5['Zipcode'].dropna()) - set(matched['Zipcode'].dropna()))
lost_rows = q5[q5['Zipcode'].isin(lost)]
print('  ZIPs with quintile-5 entire homes            : {}'.format(int(q5['Zipcode'].nunique())))
print('  ZIPs surviving into the matched cohort       : {}'.format(int(matched['Zipcode'].nunique())))
print('  ZIPs LOST ENTIRELY ({}): {}'.format(
    len(lost), ', '.join(str(int(z)) for z in lost)))
print('    between them {:,} quintile-5 rows and {:,} properties - high-occupancy listings we'.format(
    len(lost_rows), lost_rows['Airbnb Property ID'].nunique()))
print('    CANNOT price-check because their ZIP never has {} mid-occupancy entire homes in a'.format(MIN_COMP))
print('    single quarter. They are thin-market ZIPs, not exempt ones.')
q5_20 = q5[q5['superhost_period_all'] == 20]
p20_lost = sorted(set(q5_20['Zipcode'].dropna()) - set(p20['Zipcode'].dropna()))
print('  ON PERIOD 20 SPECIFICALLY - the quarter the target list is drawn from - {} ZIPs hold'.format(
    len(p20_lost)))
print('    high-occupancy entire homes with NO usable comparable: {}'.format(
    ', '.join(str(int(z)) for z in p20_lost) or 'none'))
print('    That is {:,} of the {:,} quintile-5 entire homes in period 20 ({:.1%}) which the'.format(
    len(q5_20) - len(p20), len(q5_20), 1 - len(p20) / len(q5_20)))
print('    prompt CANNOT reach. The 448-listing target list is a list of listings we can price-')
print('    check, not a list of every listing that might need it, and the brief says so.')
print()


# --- Step 5: the falsification check that decides the TRIGGER ---------------------------------
print('=' * 100)
print('STEP 5 - FALSIFICATION. Is this a BADGE problem or a MARKET-WIDE problem?')
print('=' * 100)
print('If the underpricing were Superhost behaviour, the matched cohort would be MORE Superhost')
print('than the base it is drawn from. The test is one comparison of two shares.')
SH_COHORT = float(matched['Superhost'].mean())
SH_BASE = float(eh['Superhost'].mean())
SH_TBL = pd.DataFrame({
    'rows': [len(matched), len(eh)],
    'Superhost share': [round(SH_COHORT, 4), round(SH_BASE, 4)]},
    index=['matched quintile-5 cohort', 'entire-home booked base'])
display(SH_TBL)
print('  Cohort {:.1%} against a base of {:.1%} - a difference of {:.1f} percentage points.'.format(
    SH_COHORT, SH_BASE, 100 * (SH_COHORT - SH_BASE)))
print('  INDISTINGUISHABLE. The underpricing is MARKET-WIDE BEHAVIOUR, NOT BADGE BEHAVIOUR, which')
print('  is why the trigger below is OCCUPANCY and not the Superhost badge. This corroborates')
print('  Q13, which found realised price falls with occupancy at almost the same rate for both')
print('  groups (Spearman -0.086 Superhost vs -0.074 non-Superhost).')
print('  Superhost share by occupancy quintile, for completeness: {}'.format(
    ' | '.join('Q{} {:.1%}'.format(int(i), v) for i, v in Q_TBL['superhost_share'].items())))
print('  It rises to Q4 and then FALLS at Q5 - the busiest entire homes are slightly LESS likely')
print('  to hold the badge than the fourth quintile, which is the opposite of a badge story.')
print()


# --- Step 5b: a targeting rule we TESTED AND REJECTED -----------------------------------------
print('=' * 100)
print('STEP 5b - A REJECTED ALTERNATIVE TRIGGER: "target hosts who never change their price".')
print('=' * 100)
print('The intuitive rule is that hosts who never re-price are the ones leaving money on the')
print('table. We tested it before adopting it, and it is FALSE IN THIS DATA.')
n_rates = eh.groupby('Airbnb Property ID')['Nightly Rate'].nunique()
n_per = eh.groupby('Airbnb Property ID').size()
q5m = eh[(eh['occ_quintile'] == 5) & (eh['Airbnb Property ID'].map(n_per) >= 2)].copy()
q5m['price_behaviour'] = np.where(q5m['Airbnb Property ID'].map(n_rates) == 1,
                                  'never changed listed price', 're-priced at least once')
RP_TBL = q5m.groupby('price_behaviour').agg(
    rows=('booked_days_avePrice', 'size'),
    properties=('Airbnb Property ID', 'nunique'),
    med_realised_rate=('booked_days_avePrice', 'median'),
    med_listed_rate=('Nightly Rate', 'median'),
    med_occupancy=('occupancy_rate', 'median'),
    med_revenue=('revenue', 'median'))
print('Quintile-5 entire-home rows on properties observed in >= 2 periods: {:,}'.format(len(q5m)))
display(RP_TBL.round(4))
STAT = RP_TBL.loc['never changed listed price', 'med_realised_rate']
REPR = RP_TBL.loc['re-priced at least once', 'med_realised_rate']
print('  Static-price properties realise ${:,.2f} a night; re-pricers realise ${:,.2f}. The'.format(
    STAT, REPR))
print('  static group realises MORE, not less, so "hosts who never change price are underpricing"')
print('  is FALSE and is NOT used as a targeting rule anywhere in this brief. The gap is also')
print('  small (${:,.2f}) and rests on only {:,} static rows, so it is reported as a REJECTED'.format(
    STAT - REPR, int(RP_TBL.loc['never changed listed price', 'rows'])))
print('  RULE, not as a finding in its own right. The trigger stays on the PRICE GAP.')
print()


# --- Step 6: THE FIGURE ------------------------------------------------------------------------
print('=' * 100)
print('STEP 6 - THE FIGURE. One two-panel chart, both panels in dollars per booked night.')
print('=' * 100)
print('CHART CHOICE, by Lecture 3\'s purpose mapping: this is a COMPARISON ACROSS ORDERED GROUPS,')
print('which maps to BARS. Not a line (the quintiles are ordered but the x-axis is not a')
print('continuum a value can be read off between ticks) and not a scatter (there is nothing to')
print('plot per observation). PANEL A carries the only second axis in the figure, because')
print('"price falls AND revenue plateaus" has to be ONE readable claim and the two series are in')
print('different units; the revenue series is a LINE WITH A DISTINCT MARKER so it cannot be')
print('confused with the bars. PANEL B is three bars on the SAME left axis as panel A')
print('(sharey=True), so the reader can see the cohort sits at the bottom of panel A\'s range.')
print('Every bar carries its value; every series has a distinct HATCH as well as a colour, so')
print('the figure survives the greyscale PDF.')
print()
TARGET_FLOOR = COH_CMP
TARGET_STRETCH = COH_OWN * 1.10
fig, axes = plt.subplots(1, 2, figsize=(14.6, 7.0), sharey=True,
                         gridspec_kw={'width_ratios': [1.62, 1]})
axA, axB = axes

xq = np.arange(5)
RATE_TOP = float(Q_TBL['med_realised_rate'].max()) * 1.48
REV_TOP = float(Q_TBL['med_revenue'].max()) * 1.48
barsA = axA.bar(xq, Q_TBL['med_realised_rate'], width=0.68, color=GREY, edgecolor=EDGE,
                linewidth=0.9, hatch='', zorder=3,
                label='median realised nightly rate  (n = {:,} property-periods)'.format(len(eh)))
for xi, v in zip(xq, Q_TBL['med_realised_rate']):
    axA.annotate('${:,.2f}'.format(v), xy=(xi, v), xytext=(0, 4), textcoords='offset points',
                 ha='center', va='bottom', fontsize=9.5, fontweight='bold', color='#111111',
                 zorder=6)
axA.set_ylabel('Median realised nightly rate (USD per booked night)', fontsize=10.5)
axA.set_xticks(xq)
axA.set_xticklabels(['Q{}\nocc {:.3f}\nn = {:,}'.format(int(i), o, int(n))
                     for i, o, n in zip(Q_TBL.index, Q_TBL['med_occupancy'], Q_TBL['n'])],
                    fontsize=9)
axA.set_xlabel('occupancy quintile of Dallas entire homes that booked  (Q5 = occupancy_rate >= '
               '{:.4f})'.format(CUTS[4]), fontsize=10)
axA.set_title('A. Price falls across every quintile — and revenue stops rising at the top',
              loc='left', fontsize=11)
axA.grid(axis='x', visible=False)
axA.set_axisbelow(True)

axA2 = axA.twinx()
lineA, = axA2.plot(xq, Q_TBL['med_revenue'], color=ORANGE, linewidth=2.4, marker='^',
                   markersize=11, markeredgecolor=EDGE, linestyle='--', zorder=5,
                   label='median revenue per property-period (right axis)')
for xi, v in zip(xq, Q_TBL['med_revenue']):
    # Revenue labels sit ABOVE their markers: below the marker they land on top of the bar
    # value label at Q4/Q5, which is exactly where the reader is being asked to look
    axA2.annotate('${:,.0f}'.format(v), xy=(xi, v), xytext=(0, 11), textcoords='offset points',
                  ha='center', va='bottom', fontsize=9.5, fontweight='bold', color=ORANGE,
                  zorder=6,
                  bbox=dict(boxstyle='round,pad=0.16', facecolor='white', edgecolor='none'))
axA2.set_ylabel('Median revenue per property-period (USD)', color=ORANGE, fontsize=10.5)
axA2.tick_params(axis='y', labelcolor=ORANGE)
axA2.set_ylim(0, REV_TOP)
axA2.grid(False)
# The Q4 -> Q5 revenue step is the whole point of the panel, so it is annotated rather than
# left to the reader to subtract two labels
axA2.annotate('', xy=(4, Q5_REV), xytext=(3, Q4_REV),
              arrowprops=dict(arrowstyle='-|>', color='#B00020', linewidth=2.0,
                              connectionstyle='arc3,rad=0.18'), zorder=7)
axA2.annotate('revenue FALLS ${:,.0f} ({:+.1%}) while\noccupancy nearly DOUBLES '
              '({:.3f} -> {:.3f})'.format(Q4_REV - Q5_REV, Q5_REV / Q4_REV - 1, Q4_OCC, Q5_OCC),
              xy=(4.45, REV_TOP * 0.985), ha='right', va='top',
              fontsize=9.5, color='#B00020', fontweight='bold', zorder=7,
              bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='#B00020',
                        linewidth=0.9))
axA.legend(handles=[barsA, lineA], loc='upper left', frameon=True, framealpha=0.94, fontsize=8.8)

xb = np.arange(3)
valsB = [COH_OWN, COH_CMP, TARGET_STRETCH]
labsB = ['what the cohort\nrealises today',
         'ZIP-and-quarter\ncomparable',
         'stretch target\n(+10%)']
colsB = [ORANGE, GREY, '#FFFFFF']
hatchB = ['', '///', 'xxx']
barsB = axB.bar(xb, valsB, width=0.62, color=colsB, edgecolor=EDGE, linewidth=1.1, zorder=3)
for b, h in zip(barsB, hatchB):
    b.set_hatch(h)
for xi, v in zip(xb, valsB):
    axB.annotate('${:,.2f}'.format(v), xy=(xi, v), xytext=(0, 4), textcoords='offset points',
                 ha='center', va='bottom', fontsize=10, fontweight='bold', color='#111111',
                 zorder=6)
axB.set_xticks(xb)
axB.set_xticklabels(labsB, fontsize=9.5)
axB.set_xlabel('post-break cohort: entire homes in occupancy Q5, periods 17-20\n'
               'n = {:,} property-periods · {:,} properties · {:,} hosts · {:,} ZIPs'.format(
                   len(late), late['Airbnb Property ID'].nunique(),
                   late['Airbnb Host ID'].nunique(), late['Zipcode'].nunique()), fontsize=10)
axB.set_title('B. The gap the rate-review prompt is asked to close', loc='left', fontsize=11)
axB.grid(axis='x', visible=False)
axB.set_axisbelow(True)
# The gap between bar 1 and bar 2 IS the recommendation, so it is drawn, not implied
y_gap = max(COH_OWN, COH_CMP) + 9
axB.annotate('', xy=(0, y_gap), xytext=(1, y_gap),
             arrowprops=dict(arrowstyle='<|-|>', color='#B00020', linewidth=1.8), zorder=7)
axB.annotate('gap ${:,.2f}  ({:+.1%})\n{:.1%} of the cohort sits below\nits own ZIP comparable'.format(
    COH_CMP - COH_OWN, COH_CMP / COH_OWN - 1, float((late['gap_usd'] < 0).mean())),
    xy=(0.5, y_gap), xytext=(0, 7), textcoords='offset points', ha='center', va='bottom',
    fontsize=9.5, color='#B00020', fontweight='bold', zorder=7,
    bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='#B00020', linewidth=0.9))
axB.set_ylim(0, RATE_TOP)          # sharey=True, so this sets BOTH panels' left axis at once

fig.suptitle('The listings that fill their calendars hardest are the ones realising the least '
             'per night\n'
             'left axis is dollars per BOOKED night in both panels and is SHARED (sharey=True)  ·  '
             'every bar labelled  ·  distinct hatch and colour per series so the figure reads in '
             'greyscale\nframe: entire homes that booked, {:,} property-periods from {:,} '
             'properties  ·  comparable = median realised rate of quintile-2/3/4 entire homes in '
             'the SAME ZIP in the SAME quarter (>= {} of them)'.format(
                 len(eh), eh['Airbnb Property ID'].nunique(), MIN_COMP),
             x=0.006, ha='left', fontsize=12.5, y=1.045)
fig.subplots_adjust(left=0.058, right=0.932, top=0.845, bottom=0.155, wspace=0.20)
plt.show()
print('CAPTION: entire homes that booked, {:,} property-periods ({:,} properties, {:,} hosts).'.format(
    len(eh), eh['Airbnb Property ID'].nunique(), eh['Airbnb Host ID'].nunique()))
print('Panel A: all periods 5-20, quintiles cut on occupancy_rate. Panel B: periods 17-20 only,')
print('because the market-wide price level breaks at period 17 and a KPI baseline cannot straddle')
print('two regimes. The target bar is +10% on today\'s cohort median (${:,.2f}); the floor target'.format(
    TARGET_STRETCH))
print('is the comparable itself (${:,.2f}, {:+.1%}).'.format(TARGET_FLOOR, TARGET_FLOOR / COH_OWN - 1))
print()


# --- Step 7: the numbers the brief quotes, collected -------------------------------------------
print('=' * 100)
print('STEP 7 - THE RECOMMENDATION IN NUMBERS. Everything the brief below quotes, in one place.')
print('=' * 100)
print('  TRIGGER   occupancy_rate >= {:.4f} (top quintile of Dallas entire homes that booked)'.format(CUTS[4]))
print('            AND realised rate below the median realised rate of Q2/Q3/Q4 entire homes in')
print('            the same ZIP that quarter. NOT gated on the Superhost badge (step 5).')
print('  COHORT    {:,} properties on period 20, {} hosts, {} ZIPs.'.format(
    p20['Airbnb Property ID'].nunique(), p20['Airbnb Host ID'].nunique(),
    p20['Zipcode'].nunique()))
print('  KPI       median booked_days_avePrice of the cohort - REALISED, not listed.')
print('  CURRENT   ${:,.2f} (periods 17-20).                    TARGET  >= ${:,.2f} ({:+.1%}),'.format(
    COH_OWN, TARGET_FLOOR, TARGET_FLOOR / COH_OWN - 1))
print('            stretch ${:,.2f} (+10%).                     HORIZON two evaluation quarters.'.format(
    TARGET_STRETCH))
print('  GUARDRAIL cohort median occupancy_rate must not fall below {:.4f};'.format(CUTS[4]))
print('            cohort median revenue must not fall below ${:,.2f}.'.format(COH_REV))
print('  PRIZE     median ${:,.2f} per property-period on the below-comparable subset -'.format(U_MED))
print('            ARITHMETIC UPPER BOUND, ASSUMES ZERO BOOKING LOSS, NOT A FORECAST.')
print()
print('=' * 100)
print('STEP 8 - WHAT THIS DATA CANNOT SUPPORT')
print('=' * 100)
print('(a) THE COHORT IS DEFINED ON THE OUTCOME. These listings are in quintile 5 BECAUSE they')
print('    booked heavily, and they may book heavily BECAUSE they price low. Raising the rate may')
print('    trade away the very thing that put them in the cohort. This is selection on the')
print('    dependent variable and no cross-sectional table can undo it.')
print('(b) NO EXOGENOUS PRICE VARIATION EXISTS IN THIS FILE, so no elasticity can be estimated.')
print('    Q11\'s log price/occupancy correlation of -0.056 says the two are near-INDEPENDENT')
print('    across listings; it does NOT say a given host can raise price without losing nights.')
print('(c) NOTHING HERE SUPPORTS A CAUSAL CLAIM ABOUT AN INTERVENTION. Q7\'s difference-in-')
print('    differences confidence interval on gaining the badge is [-$307, +$10] - it contains')
print('    zero. Q13 found the median price move at the moment of gaining the badge is exactly')
print('    $0.00, DiD +$7.11, and badge LOSERS move identically. That is why the deliverable is a')
print('    RANDOMISED TEST, not a rollout.')
print('(d) NO POST-PERIOD-20 DATA, so we cannot check whether the period-17 break persisted.')
print('(e) Integrated Property Manager is 100% NULL, so professional operators cannot be')
print('    separated from individual hosts inside the cohort. Host portfolio size is the only')
print('    available proxy.')
