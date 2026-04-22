import * as echarts from "https://esm.sh/echarts@5";
import ecStat from "https://esm.sh/echarts-stat@1";

echarts.registerTransform(ecStat.transform.regression);

const players = ["Alexotl", "big big big big dumps", "Nenni", "shinydog"];
const style = {colors:['#31b32b', '#1e87ff', '#da1a18','#a020f0']};

let rawData = {};
let cardName = "";
window.addEventListener("DOMContentLoaded", init);
let container = document.getElementById("chart")
let chart = echarts.init(container, null, { renderer: "canvas" });  
window.addEventListener("resize", () => chart.resize());

let selectedPlayers = new Set(players);

chart.on("legendselectchanged", (e) => {
  selectedPlayers = new Set(
    Object.entries(e.selected)
      .filter(([, on]) => on)
      .map(([name]) => name)
  );
  chart.setOption(buildChart(), { replaceMerge: ["dataset", "series"] });
});




async function init() {
  const response = await fetch("../output/cards/Watcher for Tomorrow.json");
  const data = await response.json();
  readJSON(data);
  chart.setOption(buildChart()); 
}

function readJSON(data) {
    rawData = data.picks;
    cardName = data.name;
}




function buildChart() {
    let visibleData = rawData.filter(d => selectedPlayers.has(d.player))
    console.log(visibleData.map(d => [d.draft_number, d.pick_number]))

    const datasets = players.map((player) => ({
        source: visibleData
            .filter((p) => p.player === player)
            .map((p) => ({x: p.draft_number, y: p.pick_number,
                          player: p.player, pack : p.pack_number, run: p.run })),
    }));

    const wrDataset = [
        { source: visibleData.map(d => [d.draft_number, d.pick_number]) },
        {
            fromDatasetIndex: players.length,
            transform: {
                type:   "ecStat:regression",
                config: { method: "polynomial", order: 3 },
      },
    },
    ]

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
        },
        symbol: (data) => data.run ? "diamond" : "circle"
    }));

    const wrSeries = {
        type: "line",
        datasetIndex: players.length + 1,
        encode: {x:0, y:1},
        showSymbol: false,
        lineStyle: {type: "dashed"}
    }

    return {
        dataset: datasets.concat(wrDataset),
        legend: {
            data: players,
            bottom: 14,
            icon: "roundRect",
            itemWidth: 15,
            itemHeight: 10,
            /*textStyle: {
            color: "rgba(255,255,255,0.65)",
            fontSize: 12,
            fontFamily: "monospace",
            },*/
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

        series: series.concat(wrSeries),
    };

}

