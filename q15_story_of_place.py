# Q15 asks for a "story of place". Three decisions come before any chart. First, WHICH place:
# step 1 compares Neighborhood, Zipcode and census_tract on coverage and concentration and picks
# Zipcode on the evidence rather than by habit. Second, WHAT a row is: property-periods in ZIPs
# with >= 30 distinct properties - the threshold counts PROPERTIES, not rows, because this is
# panel data (the Q12 note). Third, WHAT the story is: steps 3 and 5 show place sets what a night
# is WORTH but not whether it SELLS, and step 6 shows most of the revenue spread is listing mix,
# not place. Q12 owns the Superhost neighbourhood ranking; this cell does not repeat it.

import matplotlib.ticker as mticker      # only new import in this cell: colorbar tick formats

GREY, ORANGE, EDGE = '#8C8C8C', '#DD8452', '#333333'

# --- Step 0: scope guard - what this cell does that Q12 did not ----------------------------
print('=' * 100)
print('STEP 0 - SCOPE GUARD. Q12 ranked SUPERHOST revenue and occupancy across 11 NEIGHBOURHOODS.')
print('Q15 is the superset: ALL listings, the geographic view (Latitude/Longitude), the Superhost')
print('SHARE of each area, and the BOTTOM of the distribution. Superhost revenue is NOT re-ranked')
print('here - Q12 owns it and is cross-referenced instead.')
print('=' * 100)
print()


# --- Step 1: choose the geography, and show the choice was earned ---------------------------
print('=' * 100)
print('STEP 1 - WHICH GEOGRAPHY? Three candidate columns, judged before either is used.')
print('=' * 100)
N_PROPS = df['Airbnb Property ID'].nunique()
geo_rows = []
for c in ['Neighborhood', 'Zipcode', 'census_tract']:
    per_cat = df[df[c].notna()].groupby(c)['Airbnb Property ID'].nunique()
    big = per_cat[per_cat >= 30]
    geo_rows.append({
        'geography': c,
        'categories': int(df[c].nunique()),
        'largest category': str(per_cat.idxmax()),
        'largest cat share of properties': round(per_cat.max() / N_PROPS, 4),
        'properties with a null value': int(df.loc[df[c].isna(), 'Airbnb Property ID'].nunique()),
        'categories with >= 30 properties': int(len(big)),
        'property coverage at >= 30': round(big.sum() / N_PROPS, 4)})
geo_tbl = pd.DataFrame(geo_rows).set_index('geography')
print('All {:,} rows / {:,} distinct properties. "Coverage at >= 30" is the share of ALL properties'.format(
    len(df), N_PROPS))
print('that survive a 30-distinct-property threshold on that geography.')
display(geo_tbl)
print('  DECISION: `Zipcode` IS THE ANALYSIS GEOGRAPHY.')
print('  - Neighborhood is unusable as the primary cut: it puts {:.1%} of all properties into ONE'.format(
    geo_tbl.loc['Neighborhood', 'largest cat share of properties']))
print('    bucket ("{}") and is null for {:,} properties. A "story of place" whose'.format(
    geo_tbl.loc['Neighborhood', 'largest category'],
    geo_tbl.loc['Neighborhood', 'properties with a null value']))
print('    biggest category is half the city is not a story about place.')
print('  - census_tract is too fine: {:,} categories, and only {:.1%} of properties survive the'.format(
    geo_tbl.loc['census_tract', 'categories'],
    geo_tbl.loc['census_tract', 'property coverage at >= 30']))
print('    same threshold, so a quarter of the market would be invisible.')
print('  - Zipcode: {:,} categories, ZERO nulls, largest is {:.1%} of properties, and {:,} ZIPs'.format(
    geo_tbl.loc['Zipcode', 'categories'],
    geo_tbl.loc['Zipcode', 'largest cat share of properties'],
    geo_tbl.loc['Zipcode', 'categories with >= 30 properties']))
print('    clear the threshold covering {:.1%} of properties. It is also the unit a manager can act'.format(
    geo_tbl.loc['Zipcode', 'property coverage at >= 30']))
print('    on. Neighborhood is retained as a NAME for each ZIP, not as the analysis unit.')
print()

# ZIP -> modal neighbourhood, so every ZIP can be named in prose rather than quoted as a number
named = df[df['Neighborhood'].notna()]
modal = named.groupby('Zipcode')['Neighborhood'].agg(
    lambda s: s.mode().iloc[0] if len(s.mode()) else 'unnamed')
zip_props_all = df.groupby('Zipcode')['Airbnb Property ID'].nunique()
cross = pd.DataFrame({
    'modal Neighborhood': modal,
    'properties': zip_props_all,
    'rows': df.groupby('Zipcode').size(),
    'rows with a Neighborhood': named.groupby('Zipcode').size()}).sort_values('properties',
                                                                             ascending=False)
cross.index = cross.index.astype(int).astype(str)
cross.index.name = 'zip'
_modal_cover = 100 * named.groupby('Zipcode').apply(
    lambda s: (s['Neighborhood'] == s['Neighborhood'].mode().iloc[0]).mean()
    if len(s['Neighborhood'].mode()) else np.nan, include_groups=False)
_modal_cover.index = _modal_cover.index.astype(int).astype(str)
cross['modal name covers % of named rows'] = _modal_cover.round(1)
print('ZIP -> MODAL NEIGHBORHOOD CROSSWALK, top 15 ZIPs by distinct properties')
display(cross.head(15))
print('  The last column is a warning label, not decoration: where it is low the ZIP straddles')
print('  several named areas and the modal name is a shorthand, not a definition.')
print()


# --- Step 2: build the ZIP frame, and REPORT THE FILTER --------------------------------------
print('=' * 100)
print('STEP 2 - ROW FILTERING, REPORTED. Threshold is >= 30 DISTINCT PROPERTIES per ZIP.')
print('=' * 100)
print('The threshold counts PROPERTIES, not rows, because this is panel data: a ZIP with 8')
print('properties observed in 8 periods would clear a 30-ROW test while resting on 8 listings.')
print('This is the same rule Q12 applied to neighbourhoods.')
KEEP_ZIPS = sorted(zip_props_all[zip_props_all >= 30].index)
drop_zips = sorted(zip_props_all[zip_props_all < 30].index)
mask = df['Zipcode'].isin(KEEP_ZIPS)
print('  ZIPs in the file                     : {:,}'.format(int(df['Zipcode'].nunique())))
print('  ZIPs KEPT (>= 30 properties)         : {:,}'.format(len(KEEP_ZIPS)))
print('  ZIPs DROPPED (< 30 properties)       : {:,}  ({} properties between them)'.format(
    len(drop_zips), int(zip_props_all[zip_props_all < 30].sum())))
print('  Rows kept                            : {:,} of {:,} ({:.1%})'.format(
    int(mask.sum()), len(df), mask.mean()))
print('  Rows dropped                         : {:,} ({:.1%})'.format(
    int((~mask).sum()), (~mask).mean()))
print('  Distinct properties kept             : {:,} of {:,} ({:.1%})'.format(
    df.loc[mask, 'Airbnb Property ID'].nunique(), N_PROPS,
    df.loc[mask, 'Airbnb Property ID'].nunique() / N_PROPS))
print('  Rows with a null Zipcode             : {:,}  (none - Zipcode is complete)'.format(
    int(df['Zipcode'].isna().sum())))
print('  => The threshold is nearly free: it removes {:.1%} of rows and {:.1%} of properties.'.format(
    (~mask).mean(), 1 - df.loc[mask, 'Airbnb Property ID'].nunique() / N_PROPS))
print()

# Derived columns are built on a NARROW copy and attached in ONE concat, never inserted into df
# (100+ columns), which fires PerformanceWarning: DataFrame is highly fragmented into the PDF
KEEP_COLS = ['Airbnb Property ID', 'Airbnb Host ID', 'superhost_period_all', 'Superhost',
             'Zipcode', 'Neighborhood', 'census_tract', 'Latitude', 'Longitude', 'Listing Type',
             'Nightly Rate', 'booked_days_avePrice', 'occupancy_rate', 'revenue',
             'revenue_z', 'on_market']
g = df.loc[mask, KEEP_COLS].copy()

# Distance from downtown Dallas. Equirectangular approximation - stated, not hidden
LAT0, LON0 = 32.7767, -96.7970           # Dealey Plaza / downtown Dallas
KM_PER_DEG_LAT = 111.0
KM_PER_DEG_LON = 111.0 * np.cos(np.radians(LAT0))
BANDS = ['0-2 km', '2-4 km', '4-6 km', '6-8 km', '8-12 km', '12+ km']
dist = np.sqrt((KM_PER_DEG_LAT * (g['Latitude'] - LAT0)) ** 2
               + (KM_PER_DEG_LON * (g['Longitude'] - LON0)) ** 2)
g = pd.concat([g, pd.DataFrame({
    'zip': g['Zipcode'].astype(int).astype(str),
    'dist_km': dist,
    'dist_band': pd.cut(dist, [0, 2, 4, 6, 8, 12, np.inf], labels=BANDS, right=False),
    'entire_home': (g['Listing Type'] == 'Entire home/apt'),
    'log_rate': np.log(g['Nightly Rate'].where(g['Nightly Rate'] > 0)),
    'log_revenue': np.log(g['revenue'].where(g['revenue'] > 0)),
}, index=g.index)], axis=1)
ZIP_NAME = {str(int(z)): modal.get(z, 'unnamed') for z in KEEP_ZIPS}


# --- Step 3: THE ZIP TABLE - the answer's numbers -------------------------------------------
print('=' * 100)
print('STEP 3 - THE ZIP TABLE. All {} kept ZIPs, top AND bottom, sorted by median revenue.'.format(
    len(KEEP_ZIPS)))
print('=' * 100)


def zip_table(frame):
    """One row per ZIP. Medians throughout - Q12 showed means here rank luxury outliers."""
    grp = frame.groupby('zip')
    t = grp.agg(properties=('Airbnb Property ID', 'nunique'),
                rows=('Nightly Rate', 'size'),
                med_rate=('Nightly Rate', 'median'),
                med_realised=('booked_days_avePrice', 'median'),
                med_occupancy=('occupancy_rate', 'median'),
                med_revenue=('revenue', 'median'),
                superhost_share=('Superhost', 'mean'),
                entire_home_share=('entire_home', 'mean'))
    # revenue_z on the on-market frame: idle periods enter as $0 rather than vanishing
    om = frame[frame['on_market']]
    t['med_revenue_z_onmkt'] = om.groupby('zip')['revenue_z'].median()
    t['on_market_rows'] = om.groupby('zip').size()
    t.insert(0, 'modal Neighborhood', pd.Series(ZIP_NAME).reindex(t.index))
    return t.sort_values('med_revenue', ascending=False)


zt = zip_table(g)
n_rate_null = int(g['Nightly Rate'].isna().sum())
n_occ_null = int(g['occupancy_rate'].isna().sum())
print('DENOMINATOR / MISSINGNESS GUARD, reported before the table is read:')
print('  Rows in the ZIP frame                             : {:,}'.format(len(g)))
print('  ... with a null Nightly Rate                      : {:,}'.format(n_rate_null))
print('  ... with a null occupancy_rate / revenue          : {:,} ({:.1%}) - the never-booked'.format(
    n_occ_null, n_occ_null / len(g)))
print('      periods the setup cell itemised. med_occupancy and med_revenue are computed on the')
print('      {:,} BOOKED rows; med_revenue_z_onmkt puts the idle-but-listed periods back as $0.'.format(
    len(g) - n_occ_null))
print('  ZIPs with no booked row at all (would be an empty median): {}'.format(
    int(zt['med_revenue'].isna().sum())))
print('  ZIPs with no on-market row at all                        : {}'.format(
    int(zt['med_revenue_z_onmkt'].isna().sum())))
display(zt.round(4))

print('SPREAD ACROSS THE {} ZIPs - min, max, and max/min ratio'.format(len(zt)))
spread_rows = []
for c, lab in [('med_rate', 'median Nightly Rate (listed)'),
               ('med_realised', 'median booked_days_avePrice (realised)'),
               ('med_occupancy', 'median occupancy_rate'),
               ('med_revenue', 'median revenue'),
               ('med_revenue_z_onmkt', 'median revenue_z, on-market frame'),
               ('superhost_share', 'Superhost share of rows'),
               ('entire_home_share', 'entire-home share of rows')]:
    s = zt[c].dropna()
    spread_rows.append({'measure': lab, 'min': round(s.min(), 4), 'min ZIP': s.idxmin(),
                        'max': round(s.max(), 4), 'max ZIP': s.idxmax(),
                        'max/min': round(s.max() / s.min(), 2) if s.min() > 0 else np.nan})
spread = pd.DataFrame(spread_rows).set_index('measure')
display(spread)
print('  max/min is NaN on the last row by design: ZIP {} has NO entire homes at all (share 0),'.format(
    zt['entire_home_share'].idxmin()))
print('  so the ratio has a zero denominator and is left undefined rather than filled in.')
print('  READ THE THREE HEADLINE ROWS TOGETHER. Median listed rate spans {:.2f}x across ZIPs and'.format(
    spread.loc['median Nightly Rate (listed)', 'max/min']))
print('  median revenue {:.2f}x, but median OCCUPANCY spans only {:.2f}x. Price and revenue vary'.format(
    spread.loc['median revenue', 'max/min'], spread.loc['median occupancy_rate', 'max/min']))
print('  enormously by place; how often a listing sells barely does.')
print()

# How much of each outcome does ZIP actually explain? eta-squared = between-ZIP SS / total SS
print('HOW MUCH DOES PLACE EXPLAIN? One-way eta-squared with ZIP as the factor.')
print('  eta^2 = between-ZIP sum of squares / total sum of squares = share of variance ZIP')
print('  accounts for. Logs on the two money variables because both are strongly right-skewed')
print('  (Q1 and Q6); {} rows have Nightly Rate <= 0 and {} have revenue <= 0, and those are'.format(
    int((g['Nightly Rate'] <= 0).sum()), int((g['revenue'] <= 0).sum())))
print('  excluded from the log versions rather than clipped.')


def eta_squared(frame, ycol, gcol='zip'):
    """Share of variance in ycol accounted for by gcol. Nulls dropped and counted."""
    f = frame[frame[ycol].notna()]
    y = f[ycol].to_numpy(dtype=float)
    grand = y.mean()
    sst = ((y - grand) ** 2).sum()
    grp = f.groupby(gcol)[ycol]
    ssb = float((grp.count() * (grp.mean() - grand) ** 2).sum())
    return {'n rows used': len(f), 'rows dropped (null)': len(frame) - len(f),
            'groups': int(f[gcol].nunique()), 'eta_squared': round(ssb / sst, 4)}


eta_tbl = pd.DataFrame({lab: eta_squared(g, c) for lab, c in
                        [('log(Nightly Rate)', 'log_rate'),
                         ('occupancy_rate', 'occupancy_rate'),
                         ('log(revenue)', 'log_revenue'),
                         ('Nightly Rate (raw)', 'Nightly Rate'),
                         ('revenue (raw)', 'revenue')]}).T
display(eta_tbl)
E_RATE = eta_tbl.loc['log(Nightly Rate)', 'eta_squared']
E_OCC = eta_tbl.loc['occupancy_rate', 'eta_squared']
E_REV = eta_tbl.loc['log(revenue)', 'eta_squared']
print('  => THE HEADLINE OF THIS QUESTION: ZIP EXPLAINS {:.1%} OF THE VARIANCE IN LOG PRICE BUT'.format(E_RATE))
print('  ONLY {:.1%} OF THE VARIANCE IN OCCUPANCY (log revenue {:.1%}). Place sets what a night is'.format(
    E_OCC, E_REV))
print('  WORTH. It does not set whether it SELLS. Every recommendation below follows from that')
print('  asymmetry, and step 6 shows how much of even the price gap is listing mix.')
print()


# --- Step 4: FIGURE A - the map ---------------------------------------------------------------
print('=' * 100)
print('STEP 4 - FIGURE A, THE MAP')
print('=' * 100)
print('CHART CHOICE: A TWO-PANEL LATITUDE/LONGITUDE SCATTER, ONE POINT PER DISTINCT PROPERTY.')
print('Lecture 3 maps a RELATIONSHIP / spatial-distribution question to a scatter, and a scatter is')
print('the only chart that preserves BOTH coordinates - any binning into a bar or box chart throws')
print('one of the two dimensions away. Two panels on identical axes (sharex, sharey, equal aspect)')
print('let the reader see that the two variables have DIFFERENT geographies, which is the finding.')
print('No basemap or tile package is used: the notebook has to run offline in Colab and export to')
print('PDF, and the point pattern is legible without a street map behind it.')
print('COLOUR: cividis. It is perceptually uniform AND monotonic in luminance, so it survives the')
print('greyscale PDF as a light-to-dark ramp (standing instruction 8). A diverging or rainbow map')
print('would collapse to ambiguity in print.')
print()

# One row per property. Coordinates are property-constant, so the median over periods is exact
coord_check = g.groupby('Airbnb Property ID')[['Latitude', 'Longitude']].nunique().max()
prop = g.groupby('Airbnb Property ID').agg(
    Latitude=('Latitude', 'first'), Longitude=('Longitude', 'first'),
    zip=('zip', 'first'), dist_km=('dist_km', 'first'),
    med_rate=('Nightly Rate', 'median'), med_occ=('occupancy_rate', 'median'),
    med_rev=('revenue', 'median'), superhost=('Superhost', 'mean'),
    entire_home=('entire_home', 'mean'), periods=('Nightly Rate', 'size'))
print('POINTS ON THE MAP - one per DISTINCT PROPERTY, not per row')
print('  Distinct properties in the ZIP frame     : {:,} (from {:,} property-periods)'.format(
    len(prop), len(g)))
print('  Max distinct Latitude / Longitude values within a property: {} / {} -> coordinates are'.format(
    int(coord_check['Latitude']), int(coord_check['Longitude'])))
print('    property-constant, so collapsing the panel loses no spatial information.')
coord_counts = prop.groupby(['Latitude', 'Longitude']).size()
N_DUP_POINTS = int((coord_counts > 1).sum())
N_SHARED_COORD = int(coord_counts[coord_counts > 1].sum())
MAX_AT_POINT = int(coord_counts.max())
print('  Properties sharing an EXACT coordinate with another property: {:,} across {:,} points,'.format(
    N_SHARED_COORD, N_DUP_POINTS))
print('    max {:,} properties stacked on one point. Reported here because it means the map is'.format(
    MAX_AT_POINT))
print('    partly OVERPLOTTED and the coordinates are approximate (limitation (c) in step 9).')
print('  Panel A - properties with a median Nightly Rate : {:,} (dropped: {:,})'.format(
    int(prop['med_rate'].notna().sum()), int(prop['med_rate'].isna().sum())))
print('  Panel B - properties with a median occupancy    : {:,} (dropped: {:,} - never booked in'.format(
    int(prop['med_occ'].notna().sum()), int(prop['med_occ'].isna().sum())))
print('    any observed period, so no occupancy exists to plot)')

pa = prop[prop['med_rate'].notna()]
pb = prop[prop['med_occ'].notna()]
lo_a, hi_a = pa['med_rate'].quantile([0.05, 0.95])
lo_b, hi_b = pb['med_occ'].quantile([0.05, 0.95])
print('  COLOUR SCALE CAPPED AT THE 5th-95th PERCENTILE - THE CAP IS ON THE VIEW, NOT THE DATA:')
print('    Panel A ${:,.2f} to ${:,.2f}  ({:,} properties below, {:,} above, drawn at the end colour)'.format(
    lo_a, hi_a, int((pa['med_rate'] < lo_a).sum()), int((pa['med_rate'] > hi_a).sum())))
print('    Panel B {:.3f} to {:.3f}  ({:,} below, {:,} above)'.format(
    lo_b, hi_b, int((pb['med_occ'] < lo_b).sum()), int((pb['med_occ'] > hi_b).sum())))
print()

fig, axes = plt.subplots(1, 2, figsize=(14.6, 7.4), sharex=True, sharey=True)
for ax, frame, col, vlo, vhi, cbar_lab, subtitle, fmt in [
        (axes[0], pa, 'med_rate', lo_a, hi_a, "property's median Nightly Rate (USD)",
         'A. What a night is WORTH — median listed nightly rate', '${x:,.0f}'),
        (axes[1], pb, 'med_occ', lo_b, hi_b, "property's median occupancy_rate",
         'B. How often it SELLS — median occupancy rate', '{x:.0%}')]:
    # PLOTTING ORDER, STATED AND DELIBERATELY UNBIASED: points are drawn in a RANDOM order
    # (fixed seed) rather than sorted by the coloured variable. Sorting ascending would put the
    # high values on top everywhere, which makes DENSE areas look bright in BOTH panels and
    # manufactures the very contrast this figure is supposed to test
    fr = frame.sample(frac=1.0, random_state=0)
    sc = ax.scatter(fr['Longitude'], fr['Latitude'], c=fr[col], cmap='cividis',
                    vmin=vlo, vmax=vhi, s=9, linewidths=0, alpha=0.7, zorder=3)
    ax.plot([LON0], [LAT0], marker='*', markersize=17, color='#B00020',
            markeredgecolor='white', markeredgewidth=0.9, zorder=6, linestyle='none')
    ax.annotate('downtown', xy=(LON0, LAT0), xytext=(6, 7), textcoords='offset points',
                fontsize=9, color='#B00020', fontweight='bold', zorder=6)
    ax.set_aspect('equal')
    ax.set_title(subtitle, loc='left', fontsize=11)
    ax.set_xlabel('Longitude (degrees)', fontsize=10)
    ax.grid(True, color='#E5E7EB', linewidth=0.6)
    ax.set_axisbelow(True)
    cb = fig.colorbar(sc, ax=ax, fraction=0.046, pad=0.02, extend='both')
    cb.set_label(cbar_lab, fontsize=9.5)
    cb.ax.yaxis.set_major_formatter(mticker.StrMethodFormatter(fmt))
axes[0].set_ylabel('Latitude (degrees)', fontsize=10)
fig.suptitle('Price clusters. Occupancy does not.\n'
             'one point per distinct property  ·  n = {:,} properties (A) and {:,} (B)  ·  '
             'shared axes, equal aspect, no basemap  ·  cividis is monotonic in luminance so the '
             'ramp survives greyscale\ncolour capped at the 5th–95th percentile (arrows mark the '
             'clipped tails); points drawn in RANDOM order, not sorted by value  ·  ZIP '
             'explains {:.1%} of the variance in log price but {:.1%} of occupancy'.format(
                 len(pa), len(pb), E_RATE, E_OCC),
             x=0.008, ha='left', fontsize=12.5, y=1.03)
fig.subplots_adjust(left=0.055, right=0.99, top=0.87, bottom=0.09, wspace=0.02)
plt.show()
print('  READ PANEL A AS STRUCTURE AND PANEL B AS NOISE, and read A honestly: the high-rate')
print('  points form TWO clusters, not one radial gradient - the downtown core AND the affluent')
print('  north-central corridor. The single highest-rate ZIP in the whole table is {} ({}),'.format(
    zt['med_rate'].idxmax(), ZIP_NAME.get(zt['med_rate'].idxmax(), '')))
print('  median ${:,.0f} a night, and it sits {:.1f} km OUT, not downtown. So "price falls with'.format(
    zt['med_rate'].max(), g.loc[g['zip'] == zt['med_rate'].idxmax(), 'dist_km'].median()))
print('  distance" is a tendency with a large exception, and step 5 measures the tendency rather')
print('  than asserting the picture. Panel B has no structure to describe at all: the same map,')
print('  the same points, and no occupancy neighbourhood anywhere in it.')
print()

# --- Step 5: FIGURE B - the distance gradient. THIS IS THE STORY -----------------------------
print('=' * 100)
print('STEP 5 - FIGURE B, THE DISTANCE GRADIENT')
print('=' * 100)
print('DISTANCE FORMULA, PRINTED BECAUSE IT IS AN APPROXIMATION:')
print('  dist_km = sqrt( ({:.1f} * dLat)^2 + ({:.4f} * dLon)^2 ),  dLat/dLon in degrees from'.format(
    KM_PER_DEG_LAT, KM_PER_DEG_LON))
print('  downtown Dallas ({:.4f}, {:.4f}). {:.4f} = 111.0 * cos(radians({:.4f})).'.format(
    LAT0, LON0, KM_PER_DEG_LON, LAT0))
print('  This is the EQUIRECTANGULAR approximation - it treats a small patch of the earth as flat.')
print('  Over a city the size of Dallas the error against a great-circle distance is well under')
print('  1%, but it is an approximation and the bands below are read as coarse, not surveyed.')
print('  Observed range: {:.2f} to {:.2f} km, median {:.2f} km.'.format(
    g['dist_km'].min(), g['dist_km'].max(), g['dist_km'].median()))
print()
print('CHART CHOICE: TWO LINES ON A DUAL AXIS, ACROSS DISTANCE BANDS. Distance is an ORDERED')
print('CONTINUUM, so a line is the correct TREND chart even though the axis is spatial rather than')
print('temporal - the line encodes "as you move outward", which is exactly the claim being made. A')
print('bar chart would draw six unrelated categories and hide the monotonicity. The dual axis is')
print('needed because a rate in dollars and a rate in [0,1] cannot share a scale; each y-label AND')
print('its ticks are coloured to match its series so the axes are never ambiguous, and the two')
print('series differ in COLOUR, MARKER (o vs ^) and LINESTYLE so the figure survives greyscale.')
print('The entire-home repeat is drawn as a SECOND PANEL on shared axes rather than a separate')
print('figure, because the whole point is to compare the two gradients and the house style requires')
print('multi-panel comparisons to share a y-axis.')
print()


def band_table(frame):
    """One row per distance band. observed=False keeps empty bands visible instead of silent."""
    grp = frame.groupby('dist_band', observed=False)
    t = grp.agg(rows=('Nightly Rate', 'size'),
                properties=('Airbnb Property ID', 'nunique'),
                med_rate=('Nightly Rate', 'median'),
                med_realised=('booked_days_avePrice', 'median'),
                med_occupancy=('occupancy_rate', 'median'),
                med_revenue=('revenue', 'median'),
                entire_home_share=('entire_home', 'mean'),
                superhost_share=('Superhost', 'mean')).reindex(BANDS)
    t['booked_rows'] = grp['occupancy_rate'].count().reindex(BANDS)
    return t


gb_all = band_table(g)
gb_eh = band_table(g[g['entire_home']])
print('BAND TABLE - ALL LISTINGS ({:,} rows, {:,} properties)'.format(
    len(g), g['Airbnb Property ID'].nunique()))
display(gb_all.round(4))
print('BAND TABLE - ENTIRE HOMES ONLY ({:,} rows, {:,} properties)'.format(
    int(g['entire_home'].sum()), g.loc[g['entire_home'], 'Airbnb Property ID'].nunique()))
display(gb_eh.round(4))

RATE_TOP = max(gb_all['med_rate'].max(), gb_eh['med_rate'].max()) * 1.22
OCC_TOP = max(gb_all['med_occupancy'].max(), gb_eh['med_occupancy'].max()) * 1.35
fig, axes = plt.subplots(1, 2, figsize=(14.6, 6.2), sharey=True)
right_axes = []
for ax, tbl, subtitle, n_rows in [
        (axes[0], gb_all, 'A. All listings', len(g)),
        (axes[1], gb_eh, "B. Entire home/apt only — listing mix held roughly constant",
         int(g['entire_home'].sum()))]:
    x = np.arange(len(BANDS))
    l1, = ax.plot(x, tbl['med_rate'], color=GREY, linewidth=2.2, marker='o', markersize=8,
                  markeredgecolor=EDGE, linestyle='-', zorder=4,
                  label='median Nightly Rate (USD, left axis)')
    ax.set_ylabel('median Nightly Rate (USD)', color=GREY, fontsize=10.5, fontweight='bold')
    ax.tick_params(axis='y', labelcolor=GREY)
    ax2 = ax.twinx()
    right_axes.append(ax2)
    l2, = ax2.plot(x, tbl['med_occupancy'], color=ORANGE, linewidth=2.2, marker='^',
                   markersize=9, markeredgecolor=EDGE, linestyle='--', zorder=4,
                   label='median occupancy_rate (right axis)')
    ax2.set_ylabel('median occupancy_rate', color=ORANGE, fontsize=10.5, fontweight='bold')
    ax2.tick_params(axis='y', labelcolor=ORANGE)
    ax2.grid(False)
    # The two series cross in panel B, so labels are placed by which line is HIGHER at that
    # band (compared in axis fraction, since the two axes have different units). Fixed offsets
    # collide exactly where the lines meet, which is the one place a reader looks hardest
    rate_frac = tbl['med_rate'] / RATE_TOP
    occ_frac = tbl['med_occupancy'] / OCC_TOP
    for xi, v, above in zip(x, tbl['med_rate'], rate_frac >= occ_frac):
        ax.annotate('${:,.0f}'.format(v), xy=(xi, v), xytext=(0, 11 if above else -20),
                    textcoords='offset points', ha='center', fontsize=9, color='#111111',
                    fontweight='bold', zorder=6,
                    bbox=dict(boxstyle='round,pad=0.16', facecolor='white', edgecolor='none'))
    for xi, v, above in zip(x, tbl['med_occupancy'], occ_frac > rate_frac):
        ax2.annotate('{:.3f}'.format(v), xy=(xi, v), xytext=(0, 11 if above else -20),
                     textcoords='offset points', ha='center', fontsize=9, color=ORANGE,
                     fontweight='bold', zorder=6,
                     bbox=dict(boxstyle='round,pad=0.16', facecolor='white', edgecolor='none'))
    ax.set_xticks(x)
    ax.set_xticklabels(['{}\nn = {:,}'.format(b, int(n)) for b, n in zip(BANDS, tbl['rows'])],
                       fontsize=9)
    ax.set_xlabel('straight-line distance from downtown Dallas', fontsize=10)
    ax.set_title('{}  ·  n = {:,} property-periods'.format(subtitle, n_rows),
                 loc='left', fontsize=11)
    ax.grid(axis='x', visible=False)
    ax.set_axisbelow(True)
    ax.legend(handles=[l1, l2], loc='lower left', frameon=True, framealpha=0.92, fontsize=9.5)
axes[0].set_ylim(0, RATE_TOP)
for ax2 in right_axes:
    ax2.set_ylim(0, OCC_TOP)                 # right axes matched too, so the panels are comparable
right_axes[0].set_yticklabels([])            # only the outer occupancy axis is labelled
right_axes[0].set_ylabel('')
axes[1].set_ylabel('')
fig.suptitle('Price falls with distance from downtown. Occupancy does not move.\n'
             'median listed nightly rate and median occupancy by distance band  ·  both panels '
             'share BOTH y-axes  ·  distinct colour, marker and linestyle per series\n'
             'Spearman(distance, rate) and Spearman(distance, occupancy) printed below — the '
             'second is indistinguishable from zero',
             x=0.008, ha='left', fontsize=12.5, y=1.045)
fig.subplots_adjust(left=0.062, right=0.945, top=0.845, bottom=0.135, wspace=0.06)
plt.show()

print('SPEARMAN RANK CORRELATION OF dist_km AGAINST EACH OUTCOME')
print('  Rank correlation, not Pearson: distance is bounded below at 0 and all three outcomes are')
print('  heavily right-skewed, so a monotone measure is the honest one.')
sp_rows = []
for lab, frame in [('all listings', g), ('entire homes only', g[g['entire_home']])]:
    for c in ['Nightly Rate', 'occupancy_rate', 'revenue']:
        s = frame[frame[c].notna()]
        r = stats.spearmanr(s['dist_km'], s[c])
        sp_rows.append({'frame': lab, 'y': c, 'n': len(s),
                        'rows dropped (null y)': len(frame) - len(s),
                        'spearman_rho': round(r.statistic, 4),
                        'p': '{:.2e}'.format(r.pvalue)})
sp_tbl = pd.DataFrame(sp_rows).set_index(['frame', 'y'])
display(sp_tbl)
RHO_RATE = sp_tbl.loc[('all listings', 'Nightly Rate'), 'spearman_rho']
RHO_OCC = sp_tbl.loc[('all listings', 'occupancy_rate'), 'spearman_rho']
RHO_REV = sp_tbl.loc[('all listings', 'revenue'), 'spearman_rho']
RHO_EH_RATE = sp_tbl.loc[('entire homes only', 'Nightly Rate'), 'spearman_rho']
RHO_EH_OCC = sp_tbl.loc[('entire homes only', 'occupancy_rate'), 'spearman_rho']
print('  Median listed rate across the bands, all listings : {}'.format(
    ' -> '.join('${:,.2f}'.format(v) for v in gb_all['med_rate'])))
print('  Median occupancy across the bands, all listings   : {}'.format(
    ' -> '.join('{:.3f}'.format(v) for v in gb_all['med_occupancy'])))
print('  => PRICE FALLS MONOTONICALLY ({:.0%} from the innermost band to the outermost, rho'.format(
    gb_all['med_rate'].iloc[-1] / gb_all['med_rate'].iloc[0] - 1))
print('  {:+.4f}). OCCUPANCY DOES NOT MOVE: rho {:+.4f}, and the six band medians span only'.format(
    RHO_RATE, RHO_OCC))
print('  {:.3f}-{:.3f} - a {:.1%} range from lowest to highest, with no monotone pattern at all.'.format(
    gb_all['med_occupancy'].min(), gb_all['med_occupancy'].max(),
    gb_all['med_occupancy'].max() / gb_all['med_occupancy'].min() - 1))
print('  Within ENTIRE HOMES the price gradient more than halves ({:+.4f} against {:+.4f}) - most'.format(
    RHO_EH_RATE, RHO_RATE))
print('  of the raw gradient was listing MIX, which step 6 makes visual - and the occupancy')
print('  correlation turns marginally POSITIVE ({:+.4f}). Comparing like with like, listings'.format(
    RHO_EH_OCC))
print('  further from downtown sell very slightly MORE often, not less.')
print('  Revenue sits between the two ({:+.4f}) because revenue = nights x price and only the'.format(RHO_REV))
print('  price half has a geography.')
print()
print('  THE EXCEPTION WORTH NAMING, because a monotone line invites over-reading. ZIP {} ({},'.format(
    zt['med_rate'].idxmax(), ZIP_NAME.get(zt['med_rate'].idxmax(), '')))
print('  {} properties) has the HIGHEST median listed rate in Dallas at ${:,.0f} while sitting'.format(
    int(zt.loc[zt['med_rate'].idxmax(), 'properties']), zt['med_rate'].max()))
print('  {:.1f} km out, and it has the SECOND-LOWEST median occupancy of the {} ZIPs ({:.4f} against'.format(
    g.loc[g['zip'] == zt['med_rate'].idxmax(), 'dist_km'].median(), len(zt),
    zt.loc[zt['med_rate'].idxmax(), 'med_occupancy']))
print('  a {:.4f} median across ZIPs). Highest price, near-lowest occupancy: the distance line is a'.format(
    zt['med_occupancy'].median()))
print('  TENDENCY, and the priciest place in the city is the one that breaks it. It is also the')
print('  single clearest pricing target in the table, and the brief below names it.')
print()

# --- Step 6: FIGURE C - the mix trap, made visual --------------------------------------------
print('=' * 100)
print('STEP 6 - FIGURE C, THE MIX TRAP. Is the ZIP ranking a ranking of PLACES or of INVENTORY?')
print('=' * 100)
eh = g[g['entire_home']]
eh_props = eh.groupby('zip')['Airbnb Property ID'].nunique()
EH_ZIPS = sorted(eh_props[eh_props >= 30].index)
print('ROW FILTERING, REPORTED - the entire-home specification re-applies the same threshold')
print('  Entire-home rows in the ZIP frame          : {:,} of {:,} ({:.1%})'.format(
    len(eh), len(g), len(eh) / len(g)))
print('  ZIPs with >= 30 distinct ENTIRE-HOME properties : {:,} of {:,} kept ZIPs'.format(
    len(EH_ZIPS), len(KEEP_ZIPS)))
print('  ZIPs dropped at this stage                 : {} ({})'.format(
    len(KEEP_ZIPS) - len(EH_ZIPS),
    ', '.join(sorted(set(zt.index) - set(EH_ZIPS))) or 'none'))
print('  Entire-home rows retained                  : {:,}; properties {:,}'.format(
    int(eh['zip'].isin(EH_ZIPS).sum()),
    eh.loc[eh['zip'].isin(EH_ZIPS), 'Airbnb Property ID'].nunique()))
print()

zt_eh = zip_table(eh[eh['zip'].isin(EH_ZIPS)])
COMMON = [z for z in zt.index if z in zt_eh.index]        # ordered by the all-listings ranking
# Ranks are recomputed WITHIN the common 34 so the two rankings cover the same set of ZIPs;
# ranking over 39 and then restricting would compare a 39-place scale against a 34-place one
rank_all = zt.loc[COMMON, 'med_revenue'].rank(ascending=False, method='min')
rank_eh = zt_eh.loc[COMMON, 'med_revenue'].rank(ascending=False, method='min')
shift = pd.DataFrame({
    'modal Neighborhood': zt.loc[COMMON, 'modal Neighborhood'],
    'entire_home_share (all listings)': zt.loc[COMMON, 'entire_home_share'].round(3),
    'med_revenue (all)': zt.loc[COMMON, 'med_revenue'],
    'rank (all listings)': rank_all.astype(int),
    'med_revenue (entire homes)': zt_eh.loc[COMMON, 'med_revenue'],
    'rank (entire homes)': rank_eh.astype(int)})
shift['places moved'] = (shift['rank (all listings)'] - shift['rank (entire homes)']).astype(int)
shift = shift.sort_values('rank (all listings)')
print('THE TWO RANKINGS SIDE BY SIDE, all {} ZIPs common to both specifications'.format(len(COMMON)))
print('  A POSITIVE "places moved" means the ZIP ranks BETTER once only entire homes are compared.')
display(shift)

r_share_rev = zt['entire_home_share'].corr(zt['med_revenue'])
r_share_rate = zt['entire_home_share'].corr(zt['med_rate'])
rho_ranks = stats.spearmanr(rank_all, rank_eh)
big_moves = int(shift['places moved'].abs().ge(3).sum())
sp_all = zt.loc[COMMON]
sp_eh = zt_eh.loc[COMMON]
print('HOW MUCH OF THE ZIP REVENUE RANKING IS LISTING MIX?')
print('  Pearson(entire-home share, median revenue) across the {} ZIPs : {:+.4f}  (r^2 = {:.3f})'.format(
    len(zt), r_share_rev, r_share_rev ** 2))
print('  Pearson(entire-home share, median rate)   across the {} ZIPs : {:+.4f}  (r^2 = {:.3f})'.format(
    len(zt), r_share_rate, r_share_rate ** 2))
print('  Spearman between the two RANKINGS ({} ZIPs)                  : {:+.4f} (p = {:.4f})'.format(
    len(COMMON), rho_ranks.statistic, rho_ranks.pvalue))
print('  ZIPs moving >= 3 rank places                                : {} of {}'.format(
    big_moves, len(COMMON)))
print()
print('  SPREAD UNDER EACH SPECIFICATION - the number that matters most in this cell.')
print('  THREE columns, not two, and the middle one is the reason. The entire-home threshold drops')
print('  5 ZIPs, and those 5 contain BOTH extremes of the all-listings table, so comparing the')
print('  39-ZIP spread against the 34-ZIP entire-home spread would credit the listing-type control')
print('  with an attenuation that is really a change of ZIP set. The middle column holds the ZIP')
print('  set fixed so the last step is a clean like-for-like control.')


def spread_of(frame):
    return {'min median revenue': frame['med_revenue'].min(),
            'max median revenue': frame['med_revenue'].max(),
            'max/min revenue': frame['med_revenue'].max() / frame['med_revenue'].min(),
            'min median rate': frame['med_rate'].min(),
            'max median rate': frame['med_rate'].max(),
            'max/min rate': frame['med_rate'].max() / frame['med_rate'].min()}


ratio_tbl = pd.DataFrame({
    '(1) all listings, all {} ZIPs'.format(len(zt)): spread_of(zt),
    '(2) all listings, the {} common ZIPs'.format(len(COMMON)): spread_of(sp_all),
    '(3) entire homes, the {} common ZIPs'.format(len(COMMON)): spread_of(sp_eh)}).round(3)
display(ratio_tbl)
C1, C2, C3 = ratio_tbl.columns
RATIO_REV_39 = ratio_tbl.loc['max/min revenue', C1]
RATIO_RATE_39 = ratio_tbl.loc['max/min rate', C1]
RATIO_REV_ALL = ratio_tbl.loc['max/min revenue', C2]
RATIO_RATE_ALL = ratio_tbl.loc['max/min rate', C2]
RATIO_REV_EH = ratio_tbl.loc['max/min revenue', C3]
RATIO_RATE_EH = ratio_tbl.loc['max/min rate', C3]
print('  DECOMPOSED: revenue spread {:.1f}x -> {:.1f}x -> {:.1f}x and rate spread {:.1f}x -> {:.1f}x'.format(
    RATIO_REV_39, RATIO_REV_ALL, RATIO_REV_EH, RATIO_RATE_39, RATIO_RATE_ALL))
print('  -> {:.1f}x. The FIRST step ({:.1f}x -> {:.1f}x on revenue) is dropping 5 small ZIPs, which is'.format(
    RATIO_RATE_EH, RATIO_REV_39, RATIO_REV_ALL))
print('  a SAMPLE change, not a mix control - and those 5 are themselves a mix story: the bottom ZIP')
print('  {} has a {:.0%} entire-home share, i.e. it has essentially no entire homes to compare.'.format(
    zt['med_revenue'].idxmin(), zt['entire_home_share'].min()))
print('  The SECOND step ({:.1f}x -> {:.1f}x on revenue, {:.1f}x -> {:.1f}x on rate) is the actual'.format(
    RATIO_REV_ALL, RATIO_REV_EH, RATIO_RATE_ALL, RATIO_RATE_EH))
print('  listing-type control, on a fixed set of ZIPs.')
print('  => A REAL BUT MUCH SMALLER PLACE EFFECT SURVIVES UNDERNEATH A LARGE MIX EFFECT. The claim')
print('  "location drives revenue {:.0f}x" is FALSE and is not made anywhere in this cell; the'.format(
    RATIO_REV_39))
print('  defensible claim is a ~{:.1f}x place effect on revenue and ~{:.1f}x on price once like is'.format(
    RATIO_REV_EH, RATIO_RATE_EH))
print('  compared with like. This is the same correction Q12 found at neighbourhood level')
print('  (r = +0.822 there, {:+.3f} here) - two geographies, one conclusion.'.format(r_share_rev))
print()
print('CHART CHOICE: A HORIZONTAL DUMBBELL (SLOPE) CHART. This is a COMPARISON of two RANKINGS of')
print('the SAME categories, and a dumbbell draws the SHIFT itself - the segment between the two')
print('markers IS the finding. The alternative, two bar charts side by side, makes the reader diff')
print('34 pairs of bars by eye, which is exactly the work a chart is supposed to do for them.')
print('Markers differ in colour AND shape (o = all listings, ^ = entire homes only), and the')
print('connecting segment is hatched-equivalent by linestyle, so the figure reads in greyscale.')

fig, ax = plt.subplots(figsize=(12.4, 11.2))
ypos = np.arange(len(shift))[::-1]
ra = shift['rank (all listings)'].to_numpy()
re = shift['rank (entire homes)'].to_numpy()
for y, a, b in zip(ypos, ra, re):
    ax.plot([a, b], [y, y], color=EDGE, linewidth=1.5, alpha=0.55, zorder=2,
            linestyle='-' if abs(a - b) >= 3 else ':')
ax.scatter(ra, ypos, s=95, color=GREY, edgecolor=EDGE, linewidth=0.9, marker='o', zorder=4,
           label='rank on ALL listings')
ax.scatter(re, ypos, s=105, color=ORANGE, edgecolor=EDGE, linewidth=0.9, marker='^', zorder=5,
           label='rank on ENTIRE HOMES only')
for y, a, b in zip(ypos, ra, re):
    if abs(a - b) >= 3:
        # label sits on the far side of the entire-home marker, and carries an explicit sign:
        # + = ranks BETTER on entire homes only, - = ranks WORSE
        ax.annotate('{:+d}'.format(int(a - b)), xy=(b, y), xytext=(12 if b < a else -12, 0),
                    textcoords='offset points', ha='left' if b < a else 'right', va='center',
                    fontsize=9, color='#111111', fontweight='bold')
ax.set_yticks(ypos)
ax.set_yticklabels(['{}  {}  (EH share {:.0%})'.format(z, ZIP_NAME.get(z, ''), s)
                    for z, s in zip(shift.index, shift['entire_home_share (all listings)'])],
                   fontsize=9)
ax.set_xlim(0.2, len(shift) + 0.8)
ax.set_xlabel('rank by median revenue among these {} ZIPs   (1 = highest)'.format(len(shift)),
              fontsize=10.5)
ax.grid(axis='y', visible=False)
ax.grid(axis='x', color='#E5E7EB', linewidth=0.7)
ax.set_axisbelow(True)
ax.legend(frameon=True, framealpha=0.95, fontsize=10, loc='upper right')
ax.set_title('Most of the ZIP revenue ranking is a ranking of INVENTORY, not of place\n'
             'each ZIP\'s rank on all listings (o) against its rank on entire homes only (^)  ·  '
             '{} of {} ZIPs move >= 3 places (solid connectors)  ·  Spearman between the two '
             'rankings {:+.3f}\nholding these same {} ZIPs fixed, the revenue spread collapses '
             '{:.1f}x -> {:.1f}x and the rate spread {:.1f}x -> {:.1f}x once listing type is '
             'controlled'.format(
                 big_moves, len(shift), rho_ranks.statistic, len(shift), RATIO_REV_ALL,
                 RATIO_REV_EH, RATIO_RATE_ALL, RATIO_RATE_EH),
             loc='left', fontsize=12.5, pad=14)
fig.subplots_adjust(left=0.30, right=0.985, top=0.915, bottom=0.055)
plt.show()
print()

# --- Step 7: regime check - Q13 found a structural break at period 17 ------------------------
print('=' * 100)
print('STEP 7 - REGIME CHECK. Q13 found the market-wide listed price halves at period 17, so any')
print('pooled price figure here spans TWO regimes and has to be split before it is believed.')
print('=' * 100)
early = g[g['superhost_period_all'] < 17]
late = g[g['superhost_period_all'] >= 17]
print('  Periods 5-16 ("early") : {:,} rows, {:,} properties, periods {}-{}'.format(
    len(early), early['Airbnb Property ID'].nunique(),
    int(early['superhost_period_all'].min()), int(early['superhost_period_all'].max())))
print('  Periods 17-20 ("late") : {:,} rows, {:,} properties, periods {}-{}'.format(
    len(late), late['Airbnb Property ID'].nunique(),
    int(late['superhost_period_all'].min()), int(late['superhost_period_all'].max())))
print('  MARKET-WIDE MEDIAN LISTED RATE: ${:,.2f} (early) -> ${:,.2f} (late), a {:.1%} fall.'.format(
    early['Nightly Rate'].median(), late['Nightly Rate'].median(),
    late['Nightly Rate'].median() / early['Nightly Rate'].median() - 1))
print('  Median occupancy {:.4f} -> {:.4f}; median revenue ${:,.0f} -> ${:,.0f}.'.format(
    early['occupancy_rate'].median(), late['occupancy_rate'].median(),
    early['revenue'].median(), late['revenue'].median()))
print()
reg_rows = []
for c in ['Nightly Rate', 'occupancy_rate', 'revenue']:
    a = early.groupby('zip')[c].median()
    b = late.groupby('zip')[c].median()
    j = pd.concat([a.rename('early'), b.rename('late')], axis=1).dropna()
    r = stats.spearmanr(j['early'], j['late'])
    reg_rows.append({'measure': c, 'ZIPs in both halves': len(j),
                     'ZIPs dropped (missing a half)': len(KEEP_ZIPS) - len(j),
                     'median early': round(float(j['early'].median()), 4),
                     'median late': round(float(j['late'].median()), 4),
                     'Spearman(early rank, late rank)': round(r.statistic, 4),
                     'p': '{:.2e}'.format(r.pvalue)})
reg_tbl = pd.DataFrame(reg_rows).set_index('measure')
print('IS THE GEOGRAPHIC ORDERING STABLE ACROSS THE BREAK? Per-ZIP medians in each half, ranked.')
display(reg_tbl)
RHO_REG_RATE = reg_tbl.loc['Nightly Rate', 'Spearman(early rank, late rank)']
RHO_REG_OCC = reg_tbl.loc['occupancy_rate', 'Spearman(early rank, late rank)']
RHO_REG_REV = reg_tbl.loc['revenue', 'Spearman(early rank, late rank)']
print('  => THE LEVEL MOVES, THE ORDERING LARGELY HOLDS. Revenue is the most stable geography')
print('  (rho {:+.3f}), listed rate is moderately stable ({:+.3f}), and OCCUPANCY IS THE LEAST'.format(
    RHO_REG_REV, RHO_REG_RATE))
print('  STABLE ({:+.3f}) - which is the same finding as step 3 from a different angle: there is'.format(
    RHO_REG_OCC))
print('  so little between-ZIP signal in occupancy ({:.1%} of variance) that its ranking is mostly'.format(E_OCC))
print('  noise and does not reproduce across halves.')
print('  ANY POOLED PRICE FIGURE IN THIS CELL SPANNING PERIODS 5-20 AVERAGES TWO REGIMES. The')
print('  levels in the step 3 table and the step 5 bands are pooled and should be read as')
print('  RELATIVE positions, not as a price a manager could quote today.')
print()


# --- Step 8: Superhost share as a geography - the piece Q12 does not own ----------------------
print('=' * 100)
print('STEP 8 - SUPERHOST SHARE AS A GEOGRAPHY. Q12 ranked Superhost REVENUE; nobody has looked')
print('at where Superhosts ARE.')
print('=' * 100)
sh_cols = ['modal Neighborhood', 'properties', 'rows', 'superhost_share', 'med_rate',
           'med_occupancy', 'med_revenue', 'entire_home_share']
sh = zt[sh_cols].sort_values('superhost_share', ascending=False)
print('TOP 8 ZIPs BY SUPERHOST SHARE')
display(sh.head(8).round(4))
print('BOTTOM 8 ZIPs BY SUPERHOST SHARE')
display(sh.tail(8).round(4))
print('  Superhost share spans {:.1%} ({} {}) to {:.1%} ({} {}) -'.format(
    sh['superhost_share'].min(), sh.index[-1], ZIP_NAME.get(sh.index[-1], ''),
    sh['superhost_share'].max(), sh.index[0], ZIP_NAME.get(sh.index[0], '')))
print('  a {:.0f}x range, the widest of any measure in this cell and far wider than price.'.format(
    sh['superhost_share'].max() / sh['superhost_share'].min()))
rho_sh_rate = stats.spearmanr(zt['superhost_share'], zt['med_rate'])
rho_sh_occ = stats.spearmanr(zt.dropna(subset=['med_occupancy'])['superhost_share'],
                             zt.dropna(subset=['med_occupancy'])['med_occupancy'])
rho_sh_dist = stats.spearmanr(
    zt['superhost_share'],
    g.groupby('zip')['dist_km'].median().reindex(zt.index))
print('  Spearman(Superhost share, median rate)      across ZIPs: {:+.4f} (p = {:.3f})'.format(
    rho_sh_rate.statistic, rho_sh_rate.pvalue))
print('  Spearman(Superhost share, median occupancy) across ZIPs: {:+.4f} (p = {:.3f})'.format(
    rho_sh_occ.statistic, rho_sh_occ.pvalue))
print('  Spearman(Superhost share, ZIP median distance from downtown): {:+.4f} (p = {:.3f})'.format(
    rho_sh_dist.statistic, rho_sh_dist.pvalue))
print()
sh_band = g.groupby('dist_band', observed=False).agg(
    rows=('Superhost', 'size'), properties=('Airbnb Property ID', 'nunique'),
    superhost_share=('Superhost', 'mean'), entire_home_share=('entire_home', 'mean'),
    med_rate=('Nightly Rate', 'median'), med_occupancy=('occupancy_rate', 'median')).reindex(BANDS)
print('SUPERHOST SHARE BY DISTANCE BAND')
display(sh_band.round(4))
peak_band = sh_band['superhost_share'].idxmax()
print('  THE SHAPE, NOT A DIRECTION. Superhost share across the six bands:')
print('    {}'.format(' -> '.join('{:.1%}'.format(v) for v in sh_band['superhost_share'])))
print('  It RISES from {:.1%} in the innermost band to a peak of {:.1%} in the {} band, then falls'.format(
    sh_band['superhost_share'].iloc[0], sh_band['superhost_share'].max(), peak_band))
print('  back to {:.1%} at the edge. That is an INVERTED U, not a gradient, so "Superhosts cluster'.format(
    sh_band['superhost_share'].iloc[-1]))
print('  downtown" and "Superhosts cluster in the suburbs" are BOTH wrong. The lowest Superhost')
print('  share sits in the highest-priced, most entire-home, most downtown band - consistent with')
print('  the professional/serviced-apartment operators Q14 found, who run many listings and clear')
print('  the badge less often. This cell reports the shape and does not assert a mechanism.')
print()


# --- Step 8b: the operational shortlist the brief names --------------------------------------
# The brief below has to name ZIPs, so the shortlist is COMPUTED here rather than eyeballed off
# the table. Rule, fixed before looking: a ZIP is a PRICING CANDIDATE if its median occupancy is
# ABOVE the cross-ZIP median AND its median realised rate (booked_days_avePrice) is BELOW the
# cross-ZIP median - it sells at least as often as the typical Dallas ZIP while realising less
# per night. The mirror case, high rate and low occupancy, is the over-priced side
print('=' * 100)
print('STEP 8b - THE OPERATIONAL SHORTLIST. Computed, not eyeballed, because the brief names ZIPs.')
print('=' * 100)
MED_OCC = float(zt['med_occupancy'].median())
MED_REALISED = float(zt['med_realised'].median())
print('  Cross-ZIP medians used as the two cut lines: occupancy {:.4f}, realised rate ${:,.2f}.'.format(
    MED_OCC, MED_REALISED))
print('  RULE FIXED BEFORE LOOKING: "sells often, realises little" = median occupancy ABOVE the')
print('  first line AND median realised rate BELOW the second. This is a POSITIONING screen, not a')
print('  causal claim - it says these ZIPs look under-priced RELATIVE TO THE REST OF DALLAS.')
quad = pd.Series(np.where(
    zt['med_occupancy'] >= MED_OCC,
    np.where(zt['med_realised'] < MED_REALISED, 'sells often, realises little',
             'sells often, realises a lot'),
    np.where(zt['med_realised'] >= MED_REALISED, 'sells rarely, realises a lot',
             'sells rarely, realises little')), index=zt.index)
print()
print('  ZIPs per quadrant:')
for k, v in quad.value_counts().items():
    print('    {:<32} {:>2} ZIPs'.format(k, v))
under = zt.loc[quad == 'sells often, realises little'].sort_values('med_occupancy',
                                                                   ascending=False)
over = zt.loc[quad == 'sells rarely, realises a lot'].sort_values('med_realised',
                                                                  ascending=False)
SHOW = ['modal Neighborhood', 'properties', 'med_rate', 'med_realised', 'med_occupancy',
        'med_revenue', 'superhost_share', 'entire_home_share']
print()
print('  CANDIDATE ZIPs - SELL OFTEN, REALISE LITTLE (the pricing upside the brief targets)')
display(under[SHOW].round(4))
u_props = int(under['properties'].sum())
u_hosts = g.loc[g['zip'].isin(under.index), 'Airbnb Host ID'].nunique()
print('    {} ZIPs, {:,} distinct properties, {:,} distinct hosts. Median realised rate across'.format(
    len(under), u_props, u_hosts))
print('    these ZIPs ${:,.2f} against ${:,.2f} across all {} ZIPs; median occupancy {:.4f}'.format(
    float(under['med_realised'].median()), MED_REALISED, len(zt),
    float(under['med_occupancy'].median())))
print('    against {:.4f}.'.format(MED_OCC))
print()
print('  THE MIRROR CASE - SELL RARELY, REALISE A LOT (where a price cut, not a rise, is indicated)')
display(over[SHOW].round(4))
o_props = int(over['properties'].sum())
print('    {} ZIPs, {:,} properties. This is the smaller and more fragile group, and {} sits in'.format(
    len(over), o_props, over.index[0]))
print('    it: highest listed rate in Dallas (${:,.0f}) on {} properties with median occupancy'.format(
    float(over['med_rate'].iloc[0]), int(over['properties'].iloc[0])))
print('    {:.4f}.'.format(float(over['med_occupancy'].iloc[0])))
print()

# --- Step 9: what this data cannot support ---------------------------------------------------
print('=' * 100)
print('STEP 9 - LIMITATIONS. Four, each one attached to a specific number above.')
print('=' * 100)
print('(a) LOCATION IS NOT RANDOMLY ASSIGNED. Hosts and developers choose where to list, so the')
print('    downtown price premium is confounded with unit type, unit size and the concentration of')
print('    professional operators. Step 6 shows this is not hypothetical: entire-home share alone')
print('    correlates {:+.3f} with median ZIP revenue and {:+.3f} with median rate, and holding'.format(
    r_share_rev, r_share_rate))
print('    listing type constant collapses the revenue spread {:.1f}x -> {:.1f}x on a fixed set of'.format(
    RATIO_REV_ALL, RATIO_REV_EH))
print('    {} ZIPs (and the headline {:.1f}x spread across all {} ZIPs is bounded at the bottom by a'.format(
    len(COMMON), RATIO_REV_39, len(zt)))
print('    ZIP with no entire homes in it at all). THE CORRECT CLAIM IS ASSOCIATION:')
print('    "listings in ZIP 75201 realise a higher median rate", NEVER "location causes price".')
print('(b) revenue AND occupancy_rate ARE MECHANICALLY LINKED. Q11 measured Spearman +0.544')
print('    between them at property-period level, and revenue = booked nights x realised rate by')
print('    construction. So "place drives revenue" and "place drives bookings" are NOT independent')
print('    findings, and the revenue geography here is largely the price geography re-expressed.')
print('(c) THE COORDINATES ARE APPROXIMATE. They are property-constant (checked in step 4), but')
print('    {:,} properties share an EXACT Latitude/Longitude pair with at least one other property'.format(
    N_SHARED_COORD))
print('    across {:,} such points, with as many as {:,} properties stacked on a single point -'.format(
    N_DUP_POINTS, MAX_AT_POINT))
print('    consistent with anonymisation or building-level rounding rather than surveyed')
print('    positions. The map shows APPROXIMATE locations, and dense points are partly overplotted.')
print('(d) ZIP BOUNDARIES ARE ADMINISTRATIVE, NOT ECONOMIC. They were drawn for mail delivery, and')
print('    the {} kept ZIPs vary from {:,} to {:,} properties. A different geography would give a'.format(
    len(zt), int(zt['properties'].min()), int(zt['properties'].max())))
print('    somewhat different ranking - this is the MODIFIABLE AREAL UNIT PROBLEM, and step 1')
print('    showed the three available geographies disagree about how finely Dallas divides. The')
print('    distance gradient in step 5 is the more robust statement precisely because it does not')
print('    depend on any boundary.')
print('    Two further limits worth naming: the panel is unbalanced (rows are property-periods, so')
print('    a ZIP with long-lived listings is over-weighted relative to one with churn), and every')
print('    figure here is pooled over periods 5-20, which step 7 showed spans two price regimes.')
