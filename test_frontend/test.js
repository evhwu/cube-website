//import * as echarts from "https://cdn.jsdelivr.net/npm/echarts@6.0.0/dist/echarts.min.js";
import * as echarts from "https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.esm.min.js";



window.addEventListener("DOMContentLoaded", init);

async function init() {
  const response = await fetch("../output/cards/Lightning Bolt.json");
  const data = await response.json();
  readJSON(data);
}

function readJSON(data) {
    let cardName = data.name;
    
    const players = ["Alexotl", "big big big big dumps", "Nenni", "shinydog"];
    const style = {colors:['#31b32b', '#1e87ff', '#da1a18','#a020f0']};

    const datasets = players.map((player) => ({
        source: data.picks
            .filter((p) => p.player === player)
            .map((p) => ({x: p.draft_number, y: p.pick_number,
                          player: p.player, pack : p.pack_number, run: p.run })),
    }));

    const series = players.map((p, i ) => ({
        type : "scatter",
        name: p,
        datasetIndex : i,
        encode: { x: "x", y: "y", tooltip: ["player", "x", "y", "pack"] },
        itemStyle: {
            color: style.colors[i]
        },
        emphasis: {
            scale: 1.6
        }
    }));

    const option = {
        dataset: datasets,
        legend: {
            data: players,
            bottom: 14,
            icon: "circle",
            itemWidth: 10,
            itemHeight: 10,
            textStyle: {
            color: "rgba(255,255,255,0.65)",
            fontSize: 12,
            fontFamily: "monospace",
            },
            selectedMode: true, // click to toggle categories
        },
        xAxis: {},
        yAxis: {},
        tooltip: {
            trigger: "item",
            formatter: (params) => {
                const d = params.data;
                return (
                    `<b style="color:${style.colors[players.indexOf(d.player)]}">${d.player}</b><br/>` +
                    `x : ${d.x}<br/>` +
                    `y : ${d.y}<br/>` +
                    `size : ${d.size}`
      );
            }
        },
        grid: {
            containLabel: true
        },

        series,
    };
    let chart = echarts.init(document.getElementById("chart"));
    chart.setOption(option);   
    window.addEventListener("resize", () => chart.resize());
}

