"""
Budgeteer Insights and Visualizations

Provides comprehensive budget analysis and visualization of committed data only.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import altair as alt
from typing import List, Tuple


def prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare dataframe for analysis - ensure correct types and normalize boolean values.
    
    Args:
        df: Raw budget dataframe
    
    Returns:
        Cleaned dataframe ready for analysis
    """
    if df.empty:
        return df
    
    df_clean = df.copy()
    
    # Normalize types
    try:
        if "Amount" in df_clean.columns:
            df_clean["Amount"] = pd.to_numeric(df_clean["Amount"], errors="coerce")
        if "Day" in df_clean.columns:
            df_clean["Day"] = pd.to_numeric(df_clean["Day"], errors="coerce").astype(int)
    except:
        pass
    
    # Normalize boolean values (handle both True/False strings and actual bools)
    for col in ["Automatic", "Paid", "Cleared"]:
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].astype(str).str.lower().isin(["true", "yes", "1"])
    
    return df_clean


def get_income_summary(df: pd.DataFrame) -> Tuple[float, List[str], List[float]]:
    """Get total income and breakdown by source."""
    if df.empty or "Category" not in df.columns:
        return 0.0, [], []
    
    income_df = df[df["Category"] == "Income"]
    
    if income_df.empty:
        return 0.0, [], []
    
    total = float(income_df["Amount"].sum())
    descriptions = income_df["Description"].unique().tolist()
    amounts = [float(income_df[income_df["Description"] == d]["Amount"].sum()) for d in descriptions]
    
    return total, descriptions, amounts


def get_expense_summary(df: pd.DataFrame) -> Tuple[float, List[str], List[float]]:
    """Get total expenses and breakdown by category."""
    if df.empty or "Category" not in df.columns:
        return 0.0, [], []
    
    expense_df = df[df["Category"] != "Income"]
    
    if expense_df.empty:
        return 0.0, [], []
    
    total = float(expense_df["Amount"].sum())
    categories = expense_df["Category"].unique().tolist()
    amounts = [float(expense_df[expense_df["Category"] == c]["Amount"].sum()) for c in categories]
    
    return total, categories, amounts


def render_summary_section(df: pd.DataFrame) -> None:
    """Render summary metrics section."""
    if df.empty:
        st.info("📭 No data to analyze. Add entries to your budget to see insights.", icon="ℹ️")
        return
    
    income_total, _, _ = get_income_summary(df)
    expense_total, _, _ = get_expense_summary(df)
    balance = income_total - expense_total
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("💰 Total Income", f"${income_total:,.2f}")
    
    with col2:
        st.metric("💸 Total Expenses", f"${expense_total:,.2f}")
    
    with col3:
        color = "normal" if balance >= 0 else "inverse"
        st.metric("📊 Net Balance", f"${balance:,.2f}", delta_color=color)


def render_pending_charges(df: pd.DataFrame) -> None:
    """Render pending charges analysis."""
    if df.empty:
        return
    
    with st.expander("**⏳ Pending Charges**", expanded=False):
        # Get income entries
        income_df = df[df["Category"] == "Income"]
        
        if income_df.empty:
            st.info("No income entries to analyze.")
            return
        
        income_allocations = income_df["Allocation"].unique().tolist()
        
        with st.container(height=500):
            for allocation in income_allocations:
                if pd.isna(allocation) or allocation == " ":
                    continue
                
                st.markdown(f"### {allocation}")
                
                # Get income for this allocation
                alloc_incomes = income_df[income_df["Allocation"] == allocation]
                income_names = alloc_incomes["Description"].unique().tolist()
                
                for income_name in income_names:
                    col_left, col_right = st.columns([1, 2])
                    
                    with col_left:
                        st.markdown(f"**{income_name}**")
                        is_cleared = alloc_incomes[alloc_incomes["Description"] == income_name]["Cleared"].any()
                        if is_cleared:
                            st.success("Has Cleared", icon="💲")
                        else:
                            st.info("Not Cleared", icon="🚫")
                    
                    with col_right:
                        # Find pending charges for this income
                        expenses = df[(df["Category"] != "Income") & (df["Allocation"] == income_name)]
                        pending = expenses[(expenses["Automatic"] == True) | (expenses["Paid"] == True)]
                        pending = pending[pending["Cleared"] == False]
                        
                        if not pending.empty:
                            pending_view = pending[["Day", "Description", "Category", "Amount"]].copy()
                            pending_view["Day"] = pending_view["Day"].astype(int)
                            pending_view["Amount"] = pending_view["Amount"].apply(lambda x: f"${x:,.2f}")
                            pending_view = pending_view.sort_values("Day")
                            
                            sum_pending = float(expenses[expenses["Cleared"] == False]["Amount"].sum())
                            
                            st.metric("Sum of Pending", f"${sum_pending:,.2f}")
                            st.dataframe(pending_view, use_container_width=True, hide_index=True)
                        else:
                            st.caption("No pending charges")
                    
                    st.divider()


def render_unpaid_charges(df: pd.DataFrame) -> None:
    """Render unpaid charges analysis."""
    if df.empty:
        return
    
    with st.expander("**💳 Unpaid Charges**", expanded=False):
        expense_df = df[df["Category"] != "Income"]
        
        if expense_df.empty:
            st.info("No expenses to analyze.")
            return
        
        # Get unique income allocations
        income_df = df[df["Category"] == "Income"]
        income_names = income_df["Description"].unique().tolist()
        
        with st.container(height=500):
            for income_name in income_names:
                # Unpaid charges for this income
                unpaid = expense_df[(expense_df["Allocation"] == income_name) & 
                                   (expense_df["Automatic"] == False) & 
                                   (expense_df["Paid"] == False) & 
                                   (expense_df["Cleared"] == False)]
                
                if unpaid.empty:
                    continue
                
                st.markdown(f"### {income_name}")
                
                unpaid_view = unpaid[["Day", "Description", "Category", "Amount"]].copy()
                unpaid_view["Day"] = unpaid_view["Day"].astype(int)
                unpaid_view["Amount"] = unpaid_view["Amount"].apply(lambda x: f"${x:,.2f}")
                unpaid_view = unpaid_view.sort_values("Day")
                
                sum_unpaid = float(unpaid["Amount"].sum())
                
                st.metric("Sum of Unpaid", f"${sum_unpaid:,.2f}")
                st.dataframe(unpaid_view, use_container_width=True, hide_index=True)
                st.divider()


def render_income_burndowns(df: pd.DataFrame) -> None:
    """Render income burndown charts showing balance over time."""
    if df.empty:
        return
    
    with st.expander("**📉 Income Burndowns**", expanded=False):
        income_df = df[df["Category"] == "Income"]
        
        if income_df.empty:
            st.info("No income entries to analyze.")
            return
        
        incomes = income_df["Description"].unique().tolist()
        
        with st.container(height=500):
            for income in incomes:
                col_left, col_right = st.columns([2, 1])
                
                with col_left:
                    st.markdown(f"## {income}")
                
                with col_right:
                    st.markdown("")
                
                # Calculate burndown
                income_entry = income_df[income_df["Description"] == income].iloc[0]
                income_day = int(income_entry["Day"])
                income_amount = float(income_entry["Amount"])
                
                # Build day-by-day balance
                days = list(range(1, 32))
                balances = []
                curr_balance = 0.0
                
                for day in days:
                    if day < income_day:
                        balances.append(0.0)
                    elif day == income_day:
                        curr_balance = income_amount
                        balances.append(curr_balance)
                    else:
                        # Subtract expenses for this income on this day
                        day_expenses = df[(df["Day"] == day) & (df["Allocation"] == income)]
                        curr_balance -= float(day_expenses["Amount"].sum())
                        balances.append(curr_balance)
                
                # Create chart
                chart_df = pd.DataFrame({"Day": days, "Balance": balances})
                
                with col_left:
                    chart = alt.Chart(chart_df).mark_line(
                        point=True,
                        interpolate="step-after",
                        strokeWidth=3,
                        strokeCap="round"
                    ).encode(
                        x="Day:O",
                        y=alt.Y("Balance", scale=alt.Scale(padding=20, nice=100)),
                        order="Day"
                    ).interactive()
                    
                    st.altair_chart(chart, use_container_width=True, theme=None)
                
                with col_right:
                    final_balance = balances[-1]
                    st.metric("Total Remaining", f"${final_balance:,.2f}")
                
                st.divider()


def render_data_exploration(df: pd.DataFrame) -> None:
    """Render data exploration visualizations."""
    if df.empty:
        return
    
    with st.expander("**🔍 Data Exploration**", expanded=False):
        col_left, col_middle, col_right = st.columns([2, 1, 3])
        
        # Income allocation bar chart
        with col_left:
            income_total, _, _ = get_income_summary(df)
            expense_total, _, _ = get_expense_summary(df)
            
            if income_total > 0 or expense_total > 0:
                bar_data = pd.DataFrame({
                    "Category": ["Income", "Expenses"],
                    "Amount": [income_total, expense_total]
                })
                
                st.markdown("### 📊 Income vs Expenses")
                st.bar_chart(bar_data.set_index("Category"), height=400)
        
        # Sankey diagram
        with col_right:
            _, income_sources, income_amounts = get_income_summary(df)
            _, expense_cats, expense_amounts = get_expense_summary(df)
            
            if income_sources and expense_cats:
                # Build sankey data
                source_indices = []
                target_indices = []
                values = []
                labels = income_sources + ["Total Income"] + expense_cats
                
                # Income -> Total Income
                for i, amount in enumerate(income_amounts):
                    source_indices.append(i)
                    target_indices.append(len(income_sources))
                    values.append(amount)
                
                # Total Income -> Categories
                for i, amount in enumerate(expense_amounts):
                    source_indices.append(len(income_sources))
                    target_indices.append(len(income_sources) + 1 + i)
                    values.append(amount)
                
                st.markdown("### 🌊 Income-Expense Flow")
                
                sankey = go.Sankey(
                    node={"label": labels},
                    link={
                        "source": source_indices,
                        "target": target_indices,
                        "value": values
                    },
                    textfont={"size": 12, "color": "black"}
                )
                
                fig = go.Figure(data=sankey)
                fig.update_layout(margin=dict(l=0, r=0, t=5, b=30), height=400)
                st.plotly_chart(fig, use_container_width=True, theme=None)


def render_insights_tab() -> None:
    """Render complete insights tab."""
    # Get committed data (read-only, no pending changes)
    committed_data = st.session_state.get("committed_data", pd.DataFrame())
    
    if committed_data.empty:
        st.info("📭 No committed entries yet. Add and commit budget entries to see insights.", icon="ℹ️")
        return
    
    # Prepare data
    df = prepare_data(committed_data)
    
    # Render summary section
    render_summary_section(df)
    st.divider()
    
    # Render analysis sections
    render_pending_charges(df)
    st.markdown("")
    
    render_unpaid_charges(df)
    st.markdown("")
    
    render_income_burndowns(df)
    st.markdown("")
    
    render_data_exploration(df)
