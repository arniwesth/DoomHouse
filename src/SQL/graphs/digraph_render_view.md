digraph
{
  rankdir="LR";
  { node [shape = rect]
        n19 [label="JoiningTransform × 2"];
        n1 [label="Memory"];
        n18 [label="SimpleSquashingTransform × 2"];
    subgraph cluster_0 {
      label ="CreatingSets";
      style=filled;
      color=lightgrey;
      node [style=filled,color=white];
      { rank = same;
        n8 [label="DelayedPorts"];
      }
    }
    subgraph cluster_1 {
      label ="CreatingSets";
      style=filled;
      color=lightgrey;
      node [style=filled,color=white];
      { rank = same;
        n15 [label="DelayedPorts"];
      }
    }
    subgraph cluster_2 {
      label ="CreatingSets";
      style=filled;
      color=lightgrey;
      node [style=filled,color=white];
      { rank = same;
        n31 [label="DelayedPorts"];
      }
    }
    subgraph cluster_3 {
      label ="ReadFromStorage";
      style=filled;
      color=lightgrey;
      node [style=filled,color=white];
      { rank = same;
        n10 [label="DictionarySource × 8"];
      }
    }
    subgraph cluster_4 {
      label ="ReadFromStorage";
      style=filled;
      color=lightgrey;
      node [style=filled,color=white];
      { rank = same;
        n3 [label="DictionarySource × 8"];
      }
    }
    subgraph cluster_5 {
      label ="ReadFromStorage";
      style=filled;
      color=lightgrey;
      node [style=filled,color=white];
      { rank = same;
        n26 [label="DictionarySource × 8"];
      }
    }
    subgraph cluster_6 {
      label ="Aggregating";
      style=filled;
      color=lightgrey;
      node [style=filled,color=white];
      { rank = same;
        n40 [label="AggregatingTransform"];
        n41 [label="Resize"];
      }
    }
    subgraph cluster_7 {
      label ="CreatingSet";
      style=filled;
      color=lightgrey;
      node [style=filled,color=white];
      { rank = same;
        n7 [label="CreatingSetsTransform"];
        n6 [label="Resize"];
      }
    }
    subgraph cluster_8 {
      label ="Expression";
      style=filled;
      color=lightgrey;
      node [style=filled,color=white];
      { rank = same;
        n28 [label="ExpressionTransform × 8"];
      }
    }
    subgraph cluster_9 {
      label ="Expression";
      style=filled;
      color=lightgrey;
      node [style=filled,color=white];
      { rank = same;
        n5 [label="ExpressionTransform × 8"];
      }
    }
    subgraph cluster_10 {
      label ="Expression";
      style=filled;
      color=lightgrey;
      node [style=filled,color=white];
      { rank = same;
        n12 [label="ExpressionTransform × 8"];
      }
    }
    subgraph cluster_11 {
      label ="ReadFromSystemNumbers";
      style=filled;
      color=lightgrey;
      node [style=filled,color=white];
      { rank = same;
        n34 [label="NumbersRange"];
      }
    }
    subgraph cluster_12 {
      label ="ReadFromSystemNumbers";
      style=filled;
      color=lightgrey;
      node [style=filled,color=white];
      { rank = same;
        n20 [label="NumbersRange"];
      }
    }
    subgraph cluster_13 {
      label ="Expression";
      style=filled;
      color=lightgrey;
      node [style=filled,color=white];
      { rank = same;
        n38 [label="ExpressionTransform"];
      }
    }
    subgraph cluster_14 {
      label ="Expression";
      style=filled;
      color=lightgrey;
      node [style=filled,color=white];
      { rank = same;
        n42 [label="ExpressionTransform × 8"];
      }
    }
    subgraph cluster_15 {
      label ="Filter";
      style=filled;
      color=lightgrey;
      node [style=filled,color=white];
      { rank = same;
        n4 [label="FilterTransform × 8"];
      }
    }
    subgraph cluster_16 {
      label ="Expression";
      style=filled;
      color=lightgrey;
      node [style=filled,color=white];
      { rank = same;
        n17 [label="ExpressionTransform"];
      }
    }
    subgraph cluster_17 {
      label ="Expression";
      style=filled;
      color=lightgrey;
      node [style=filled,color=white];
      { rank = same;
        n24 [label="ExpressionTransform"];
      }
    }
    subgraph cluster_18 {
      label ="Expression";
      style=filled;
      color=lightgrey;
      node [style=filled,color=white];
      { rank = same;
        n35 [label="ExpressionTransform"];
      }
    }
    subgraph cluster_19 {
      label ="Expression";
      style=filled;
      color=lightgrey;
      node [style=filled,color=white];
      { rank = same;
        n22 [label="ExpressionTransform"];
        n23 [label="FillingRightJoinSide"];
      }
    }
    subgraph cluster_20 {
      label ="Expression";
      style=filled;
      color=lightgrey;
      node [style=filled,color=white];
      { rank = same;
        n33 [label="ExpressionTransform"];
      }
    }
    subgraph cluster_21 {
      label ="Expression";
      style=filled;
      color=lightgrey;
      node [style=filled,color=white];
      { rank = same;
        n36 [label="ExpressionTransform"];
        n37 [label="FillingRightJoinSide"];
      }
    }
    subgraph cluster_22 {
      label ="Expression";
      style=filled;
      color=lightgrey;
      node [style=filled,color=white];
      { rank = same;
        n32 [label="ExpressionTransform"];
      }
    }
    subgraph cluster_23 {
      label ="Expression";
      style=filled;
      color=lightgrey;
      node [style=filled,color=white];
      { rank = same;
        n16 [label="ExpressionTransform"];
      }
    }
    subgraph cluster_24 {
      label ="Expression";
      style=filled;
      color=lightgrey;
      node [style=filled,color=white];
      { rank = same;
        n21 [label="ExpressionTransform"];
      }
    }
    subgraph cluster_25 {
      label ="Expression";
      style=filled;
      color=lightgrey;
      node [style=filled,color=white];
      { rank = same;
        n25 [label="ExpressionTransform"];
      }
    }
    subgraph cluster_26 {
      label ="Expression";
      style=filled;
      color=lightgrey;
      node [style=filled,color=white];
      { rank = same;
        n2 [label="ExpressionTransform"];
      }
    }
    subgraph cluster_27 {
      label ="CreatingSet";
      style=filled;
      color=lightgrey;
      node [style=filled,color=white];
      { rank = same;
        n14 [label="CreatingSetsTransform"];
        n13 [label="Resize"];
      }
    }
    subgraph cluster_28 {
      label ="Expression";
      style=filled;
      color=lightgrey;
      node [style=filled,color=white];
      { rank = same;
        n9 [label="ExpressionTransform"];
      }
    }
    subgraph cluster_29 {
      label ="CreatingSet";
      style=filled;
      color=lightgrey;
      node [style=filled,color=white];
      { rank = same;
        n30 [label="CreatingSetsTransform"];
        n29 [label="Resize"];
      }
    }
    subgraph cluster_30 {
      label ="Filter";
      style=filled;
      color=lightgrey;
      node [style=filled,color=white];
      { rank = same;
        n11 [label="FilterTransform × 8"];
      }
    }
    subgraph cluster_31 {
      label ="Filter";
      style=filled;
      color=lightgrey;
      node [style=filled,color=white];
      { rank = same;
        n27 [label="FilterTransform × 8"];
      }
    }
    subgraph cluster_32 {
      label ="Expression";
      style=filled;
      color=lightgrey;
      node [style=filled,color=white];
      { rank = same;
        n39 [label="ExpressionTransform"];
      }
    }
  }
  n19 -> n24 [label=""];
  n19 -> n38 [label=""];
  n1 -> n2 [label=""];
  n18 -> n19 [label="× 2"];
  n8 -> n9 [label=""];
  n15 -> n16 [label=""];
  n31 -> n32 [label=""];
  n10 -> n11 [label="× 8"];
  n3 -> n4 [label="× 8"];
  n26 -> n27 [label="× 8"];
  n40 -> n41 [label=""];
  n41 -> n42 [label="× 8"];
  n7 -> n8 [label=""];
  n6 -> n7 [label=""];
  n28 -> n29 [label="× 8"];
  n5 -> n6 [label="× 8"];
  n12 -> n13 [label="× 8"];
  n34 -> n35 [label=""];
  n20 -> n21 [label=""];
  n38 -> n39 [label=""];
  n4 -> n5 [label="× 8"];
  n17 -> n18 [label=""];
  n24 -> n25 [label=""];
  n35 -> n36 [label=""];
  n22 -> n23 [label=""];
  n23 -> n19 [label=""];
  n33 -> n18 [label=""];
  n36 -> n37 [label=""];
  n37 -> n19 [label=""];
  n32 -> n33 [label=""];
  n16 -> n17 [label=""];
  n21 -> n22 [label=""];
  n25 -> n31 [label=""];
  n2 -> n8 [label=""];
  n14 -> n15 [label=""];
  n13 -> n14 [label=""];
  n9 -> n15 [label=""];
  n30 -> n31 [label=""];
  n29 -> n30 [label=""];
  n11 -> n12 [label="× 8"];
  n27 -> n28 [label="× 8"];
  n39 -> n40 [label=""];
}