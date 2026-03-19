def main():
    import plotly.graph_objects as go
    from person import load_persons_from_file

    def node(label, x, y):
        return {"label": label, "x": x, "y": y}

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

    nodes = [
        node(f"{p1.name} Lohn", 0.01, 0.25),
        node(f"{p1.name} PK-Abzug", 1 / sections, 0.01),
        node(f"{p1.name} Wohnen - Miete", 1 / sections, 0.1),
        node(f"{p1.name} Div. Ausgaben", 1 / sections, 0.28),
        node(f"{p1.name} Sparen", 2 / sections, 0.45),
        node(f"{p2.name} Lohn", 0.01, 0.77),
        node(f"{p2.name} PK-Abzug", 1 / sections, 0.55),
        node(f"{p2.name} Wohnen - Eigentum", 1 / sections, 0.65),
        node(f"{p2.name} Div. Ausgaben", 1 / sections, 0.83),
        node(f"{p2.name} Sparen", 2 / sections, 0.99),
        node("PK Einnahmen", 3 / sections, 0.20),
        node("PK Rendite", 3 / sections, 0.12),
        node("PK Immo Amort", 3 / sections, 0.34),
        node("PK Personalkosten", 4 / sections, 0.1),
        node("Eigentum Immo Amort", 3 / sections, 0.72),
        node("Bank Rendite", 3 / sections, 0.62),
        node(f"{p1.name} Sparen Total", 4 / sections, 0.45),
        node(f"{p2.name} Sparen Total", 4 / sections, 0.99),
    ]

    duplicate_nodes = []
    seen_node_labels = set()
    for n in nodes:
        if n["label"] in seen_node_labels:
            duplicate_nodes.append(n["label"])
        seen_node_labels.add(n["label"])

    if duplicate_nodes:
        raise ValueError(f"Duplicate node definitions found: {', '.join(sorted(set(duplicate_nodes)))}")

    node_positions = {n["label"]: (n["x"], n["y"]) for n in nodes}

    missing_nodes = [label for label in labels if label not in node_positions]
    if missing_nodes:
        missing = ", ".join(missing_nodes)
        raise ValueError(f"Missing x/y position for nodes: {missing}")

    node_x = [node_positions[label][0] for label in labels]
    node_y = [node_positions[label][1] for label in labels]

    fig = go.Figure(
        data=[
            go.Sankey(
                arrangement="freeform",
                node=dict(
                    pad=16,
                    thickness=16,
                    line=dict(color="black", width=0.5),
                    label=display_labels,
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
