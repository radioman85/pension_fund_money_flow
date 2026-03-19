def main():
    import plotly.graph_objects as go
    from person import load_persons_from_file

    def node(label, x, y, color=None):
        return {"label": label, "x": x, "y": y, "color": color}

    persons = load_persons_from_file()
    if len(persons) < 2:
        raise ValueError("At least 2 persons are required in persons.json")

    p1 = persons[0]
    p2 = persons[1]


    flows = [
        (f"{p1.name} Lohn", f"{p1.name} PK-Abzug", p1.expenses.retirement.amount),
        (f"{p1.name} Lohn", f"{p1.name} Wohnen - Miete", p1.expenses.housing.amount),
        (f"{p1.name} Lohn", f"{p1.name} Div. Ausgaben", p1.expenses.living.amount),
        (f"{p1.name} Lohn", f"{p1.name} Sparen", p1.expenses.savings.amount),
        (f"{p1.name} Wohnen - Miete", "PK Rendite", 1000),
        (f"{p1.name} PK-Abzug", "PK Einnahmen", 800),
        (f"{p1.name} Wohnen - Miete", "PK Immo Amort", 1000),

        (f"{p2.name} Lohn", f"{p2.name} PK-Abzug", p2.expenses.retirement.amount),
        (f"{p2.name} Lohn", f"{p2.name} Wohnen - Eigentum", p2.expenses.housing.amount),
        (f"{p2.name} Wohnen - Eigentum", f"{p2.name} Sparen", 500),
        (f"{p2.name} Wohnen - Eigentum", "Eigentum Immo Amort", 1000),
        (f"{p2.name} Wohnen - Eigentum", "Bank Rendite", 500),
        (f"{p2.name} Lohn", f"{p2.name} Div. Ausgaben", p2.expenses.living.amount),
        (f"{p2.name} Lohn", f"{p2.name} Sparen", p2.expenses.savings.amount),
        (f"{p2.name} PK-Abzug", "PK Einnahmen", 800),

        (f"{p1.name} Sparen", f"{p1.name} Sparen Total", p1.expenses.savings.amount),
        (f"{p2.name} Sparen", f"{p2.name} Sparen Total", p2.expenses.savings.amount+500),

        ("PK Rendite", f"{p1.name} Sparen Total", 333),
        ("PK Rendite", f"{p2.name} Sparen Total", 333),
        ("PK Rendite", "PK Personalkosten", 334),
    ]
    
    labels = []
    for source_label, target_label, _ in flows:
        if source_label not in labels:
            labels.append(source_label)
        if target_label not in labels:
            labels.append(target_label)

    label_to_index = {label: index for index, label in enumerate(labels)}
    source = [label_to_index[source_label] for source_label, _, _ in flows]
    target = [label_to_index[target_label] for _, target_label, _ in flows]
    value = [amount for _, _, amount in flows]

    highlight_flow_colors = {
        (f"{p1.name} Wohnen - Miete", "PK Rendite"): "orange",
        (f"{p2.name} Wohnen - Eigentum", "Bank Rendite"): "crimson",
        (f"{p2.name} Wohnen - Eigentum", f"{p2.name} Sparen"): "green",
    }
    flow_colors = [
        highlight_flow_colors.get((source_label, target_label), "rgba(160,160,160,0.35)")
        for source_label, target_label, _ in flows
    ]

    incoming_totals = {label: 0 for label in labels}
    outgoing_totals = {label: 0 for label in labels}
    for source_label, target_label, amount in flows:
        outgoing_totals[source_label] += amount
        incoming_totals[target_label] += amount

    display_labels = [
        f"{label} (in:{incoming_totals[label]}, out:{outgoing_totals[label]}, net:{incoming_totals[label]-outgoing_totals[label]})"
        for label in labels
    ]

    sections = 4

    color_income = "#1f77b4"
    color_retirement = "#9467bd"
    color_housing = "#ff7f0e"
    color_living = "#d62728"
    color_savings = "#2ca02c"
    color_investment = "#17becf"
    color_total = "#bcbd22"

    nodes = [
        node(f"{p1.name} Lohn", 0.01, 0.25, color_income),
        node(f"{p1.name} PK-Abzug", 1 / sections, 0.01, color_retirement),
        node(f"{p1.name} Wohnen - Miete", 1 / sections, 0.1, color_housing),
        node(f"{p1.name} Div. Ausgaben", 1 / sections, 0.28, color_living),
        node(f"{p1.name} Sparen", 2 / sections, 0.45, color_savings),
        node(f"{p2.name} Lohn", 0.01, 0.77, color_income),
        node(f"{p2.name} PK-Abzug", 1 / sections, 0.55, color_retirement),
        node(f"{p2.name} Wohnen - Eigentum", 1 / sections, 0.65, color_housing),
        node(f"{p2.name} Div. Ausgaben", 1 / sections, 0.83, color_living),
        node(f"{p2.name} Sparen", 2 / sections, 0.99, color_savings),
        node("PK Einnahmen", 3 / sections, 0.20, color_retirement),
        node("PK Rendite", 3 / sections, 0.12, color_investment),
        node("PK Immo Amort", 3 / sections, 0.34, color_housing),
        node("PK Personalkosten", 4 / sections, 0.1, color_living),
        node("Eigentum Immo Amort", 3 / sections, 0.72, color_housing),
        node("Bank Rendite", 3 / sections, 0.62, color_investment),
        node(f"{p1.name} Sparen Total", 4 / sections, 0.45, color_total),
        node(f"{p2.name} Sparen Total", 4 / sections, 0.99, color_total),
    ]

    duplicate_nodes = []
    seen_node_labels = set()
    for n in nodes:
        if n["label"] in seen_node_labels:
            duplicate_nodes.append(n["label"])
        seen_node_labels.add(n["label"])

    if duplicate_nodes:
        raise ValueError(f"Duplicate node definitions found: {', '.join(sorted(set(duplicate_nodes)))}")

    node_definitions = {n["label"]: n for n in nodes}
    node_positions = {label: (n["x"], n["y"]) for label, n in node_definitions.items()}

    missing_nodes = [label for label in labels if label not in node_positions]
    if missing_nodes:
        missing = ", ".join(missing_nodes)
        raise ValueError(f"Missing x/y position for nodes: {missing}")

    node_x = [node_positions[label][0] for label in labels]
    node_y = [node_positions[label][1] for label in labels]
    node_colors = [
        node_definitions[label]["color"] if node_definitions[label]["color"] is not None else "rgba(31,119,180,0.8)"
        for label in labels
    ]

    fig = go.Figure(
        data=[
            go.Sankey(
                arrangement="freeform",
                node=dict(
                    pad=16,
                    thickness=16,
                    line=dict(color="black", width=0.5),
                    label=display_labels,
                    color=node_colors,
                    x=node_x,
                    y=node_y,
                ),
                link=dict(
                    source=source,
                    target=target,
                    value=value,
                    color=flow_colors,
                ),
            )
        ]
    )

    fig.update_layout(title_text="Real Estate vs. Pension Funds - How the money flows", font_size=10, height=900)
    fig.show()


if __name__ == "__main__":
    main()
