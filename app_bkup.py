import pandas as pd
import plotly.express as px
import streamlit as st
from logic import analyze

st.set_page_config(page_title='FoodWise | Food Rescue', page_icon='🥬', layout='wide')
st.markdown('''<style>.block-container{padding-top:2rem;max-width:1250px}h1{color:#17634a}div[data-testid="stMetric"]{background:#f1f8f3;border:1px solid #d9e9dc;border-radius:12px;padding:15px}</style>''', unsafe_allow_html=True)
st.title('🥬 FoodWise')
st.caption('Supermarket food waste rescue • A transparent, rule-based decision assistant')
st.info('**Educational simulation:** Fictional inventory and simplified assumptions. Recommendations are not food-safety decisions; always follow store policy, product-specific rules and applicable law.')

@st.cache_data
def load_sample():
    return pd.read_csv('sample_data.csv')

with st.sidebar:
    st.header('⚙️ Scenario controls')
    discount = st.slider('Discount on recommended products (%)', 0, 80, 30, 5)
    uplift = st.slider('Assumed demand increase after discount (%)', 0, 200, 50, 10)
    st.caption('Demand increase is an assumption for scenario analysis, not a prediction.')
    if st.button('Reset sample inventory', use_container_width=True):
        st.session_state['inventory'] = load_sample().copy()
        st.rerun()

if 'inventory' not in st.session_state:
    st.session_state['inventory'] = load_sample().copy()

st.subheader('1 · Edit supermarket inventory')
st.caption('Click a cell to change stock, daily demand or days to expiry. Results recalculate automatically.')
edited = st.data_editor(st.session_state['inventory'], hide_index=True, use_container_width=True, num_rows='dynamic', key='editor', column_config={
    'product':st.column_config.TextColumn('Product',required=True),
    'category':st.column_config.TextColumn('Category',required=True),
    'stock_units':st.column_config.NumberColumn('Stock (units)',min_value=0,step=1,required=True),
    'daily_demand':st.column_config.NumberColumn('Daily demand',min_value=0,step=1,required=True),
    'days_to_expiry':st.column_config.NumberColumn('Days to expiry',step=1,required=True),
    'price_eur':st.column_config.NumberColumn('Unit price (€)',min_value=0,format='€%.2f',required=True),
    'unit_weight_kg':st.column_config.NumberColumn('Unit weight (kg)',min_value=0,format='%.2f',required=True),
    'donation_eligible':st.column_config.CheckboxColumn('Donation eligible')
})
try:
    results = analyze(edited, discount, uplift)
except (ValueError, TypeError, KeyError) as exc:
    st.error(f'Please correct the inventory inputs: {exc}')
    st.stop()

st.subheader('2 · Sustainability overview')
col1,col2,col3,col4 = st.columns(4)
stock_kg = float((results.stock_units * results.unit_weight_kg).sum())
risk_kg = float(results.baseline_at_risk_kg.sum())
rescued_kg = float(results.potential_rescued_kg.sum())
revenue = float(results.estimated_revenue_eur.sum())
col1.metric('Inventory monitored', f'{stock_kg:,.1f} kg')
col2.metric('Baseline surplus at risk', f'{risk_kg:,.1f} kg')
col3.metric('Potentially rescued', f'{rescued_kg:,.1f} kg')
col4.metric('Estimated discount revenue', f'€{revenue:,.2f}')
st.caption('“Potentially rescued” includes assumed extra discount sales and eligible donations; it is not verified waste avoided. Revenue excludes costs and taxes.')

left,right = st.columns(2)
with left:
    risk_counts = results.risk.value_counts().rename_axis('Risk').reset_index(name='Products')
    fig = px.bar(risk_counts,x='Risk',y='Products',color='Risk',text='Products',category_orders={'Risk':['Expired','High','Medium','Low']},color_discrete_map={'Expired':'#7f1d1d','High':'#dc2626','Medium':'#f59e0b','Low':'#16a34a'},title='Products by expiry risk')
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig,use_container_width=True)
with right:
    actions = results.action.value_counts().rename_axis('Action').reset_index(name='Products')
    fig = px.pie(actions,names='Action',values='Products',hole=0.55,title='Recommended actions')
    st.plotly_chart(fig,use_container_width=True)

st.subheader('3 · Product recommendations')
view = results[['product','days_to_expiry','stock_units','expected_sales','surplus_units','risk','action','potential_rescued_kg','estimated_revenue_eur']].copy()
view.columns = ['Product','Days to expiry','Stock','Expected sales','Potential surplus','Risk','Recommended action','Potential rescue (kg)','Discount revenue (€)']
st.dataframe(view.sort_values(['Days to expiry','Product']),hide_index=True,use_container_width=True,column_config={'Potential rescue (kg)':st.column_config.NumberColumn(format='%.2f'),'Discount revenue (€)':st.column_config.NumberColumn(format='€%.2f')})

st.subheader('4 · What-if impact')
impact = pd.DataFrame({'Scenario':['Baseline surplus at risk','Remaining after assumed interventions'],'Kilograms':[risk_kg,max(0,risk_kg-rescued_kg)]})
fig = px.bar(impact,x='Scenario',y='Kilograms',text_auto='.1f',color='Scenario',title='Illustrative potential reduction in at-risk surplus (kg)',color_discrete_sequence=['#e9a23b','#2d966f'])
fig.update_layout(showlegend=False,yaxis_title='kg')
st.plotly_chart(fig,use_container_width=True)
if risk_kg > 0:
    st.success(f'Under these assumptions, interventions could address **{rescued_kg/risk_kg:.1%}** of the baseline surplus at risk.')
else:
    st.success('No baseline surplus at risk under the current inputs.')
st.download_button('⬇️ Download analysis CSV',results.to_csv(index=False).encode('utf-8'),'foodwise_analysis.csv','text/csv')
with st.expander('How does the decision algorithm work?'):
    st.markdown('''1. **Expected sales** = min(stock, daily demand × nonnegative days until expiry).\n2. **Surplus** = max(0, stock − expected sales).\n3. **Risk**: expired if days ≤ 0; otherwise low if no surplus; high if ≤ 1 day; medium if ≤ 3 days; low otherwise.\n4. **Action**: expired → remove; no surplus → normal sale; ≤ 1 day and donation eligible → donate surplus; ≤ 3 days → discount surplus; otherwise monitor.\n5. **Scenario**: additional discounted sales = min(surplus, expected demand × assumed demand uplift). Donation is assumed to rescue all eligible surplus. This is intentionally optimistic and not a measured outcome.''')
