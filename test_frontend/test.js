import * as echarts from "https://esm.sh/echarts@5";
import ecStat from "https://esm.sh/echarts-stat@1";
echarts.registerTransform(ecStat.transform.regression);


const players = ["Alexotl", "big big big big dumps", "Nenni", "shinydog"];
const style = {colors:['#31b32b', '#1e87ff', '#da1a18','#a020f0']};

let rawData = {};
let cardName = "";
let selectedPlayers = new Set(players);

window.addEventListener("DOMContentLoaded", init);
let container = document.getElementById("chart")
let chart = echarts.init(container, null, { renderer: "canvas" });  
window.addEventListener("resize", () => chart.resize());
chart.on("legendselectchanged", (e) => {
    selectedPlayers = new Set(
        Object.entries(e.selected)
            .filter(([, on]) => on)
            .map(([name]) => name)
    );
    chart.setOption(buildChart(), { replaceMerge: ["dataset", "series"] });
});




async function init() {
    const params = new URLSearchParams(window.location.search);
    //add a try
    const response = await fetch(`../output/cards/${params.get("card")}.json`);
    const data = await response.json();
    readJSON(data);
    chart.setOption(buildChart()); 
}

function readJSON(data) {
    rawData = data.picks;
    cardName = data.name;
}




function buildChart() {
    let visibleData = rawData.filter(d => selectedPlayers.has(d.player));

    let totals = {};
    players.forEach(p => {
        const playerPicks = visibleData.filter(d => d.player === p);
        totals[p] = {
            pick:  (playerPicks.reduce((s, d) => s + d.pick_number, 0) / playerPicks.length).toFixed(1),
            run: playerPicks.reduce((total, curr) => (curr.run ? total + 1:  total), 0),
            not_run : playerPicks.reduce((total, curr) => (!curr.run ? total + 1:  total), 0),
        };
    });
    console.log(totals)

    const datasets = players.map((player) => ({
        source: visibleData
            .filter((p) => p.player === player)
            .map((p) => ({x: p.draft_number, y: p.pick_number,
                          player: p.player, pack : p.pack_number, run: p.run,
                          rank: p.rank, deck_name: p.deck_name})),
    }));

    const wrDataset = [
        {
            source: visibleData
                .map(d => [d.draft_number, d.pick_number])
        },
        {
            fromDatasetIndex: players.length,
            transform: {
                type:   "ecStat:regression",
                config: { method: "polynomial", order: 2 },
            },
        },
        {
            source: visibleData
                .filter((d => d.run === true))
                .map(d => [d.draft_number, d.rank])
        },
        {
            fromDatasetIndex: players.length + 2,
            transform: {
                type: "ecStat:regression",
                config: {method: "polynomial", order: 2 },
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

    const wrSeries = [
        {
            type: "line",
            datasetIndex: players.length + 1,
            yAxisIndex: 0,
            encode: {x:0, y:1},
            showSymbol: false,
            lineStyle: {type: "dashed",
                        color: '#f4641d'
            },
        },
        {
            type: "line",
            datasetIndex: players.length + 3,
            yAxisIndex: 1,

            encode: {x:0, y:1},
            showSymbol: false,
            lineStyle: {type: "dashed",
                        color: '#000000'
            }
        }
    ]

    const pieSeries = [
        {
            type: "pie",
            tooltip: {
                trigger: "item",
                formatter: (params) => {
                    const pdee = params.data
                    return `<b style="color:${style.colors[players.indexOf(pdee.name)]}"> ${pdee.name}</b></br>` +
                    `Avg Pick: ${pdee.pick_rate}</br>` +
                    `Run ${pdee.run}/${pdee.value} times (${(100*pdee.run/pdee.value).toFixed(2)}%)`
                }
            },
            center: ["85%", "70%"],
            radius: ["22%", "35%"],
            data: players.map((p, i) => ({
                name: p,
                run: totals[p].run,
                not_run: totals[p].not_run,
                value: totals[p].run + totals[p].not_run,
                pick_rate: totals[p].pick,
                itemStyle: { color: style.colors[i] }
            })),
        },
    ]   

    return {
        dataset: datasets.concat(wrDataset),
        title: {
            text: cardName,
            left: "center"
        },
        legend: {
            data: players,
            bottom: 14,
            icon: "roundRect",
            itemWidth: 15,
            itemHeight: 10,
        },
        xAxis: {type: "value", name: "Draft Number", nameLocation: "middle",
            nameGap: 28, min: 17
        },
        yAxis: [
            {
                type: "value", name: "Pick Number",
                nameTextStyle: {color: '#f4641d'},
                min: 1, max: 15
            },
            {
                type: "value", name: "Rank",
                splitLine: { show: false },
                nameTextStyle: {color: '#000000'},
                min: 1, max : 4
            },
        ],
        tooltip: {
            trigger: "axis",
            axisPointer : {
                type: "line",
                snap: true,
                crossStyle: {
                    type: "dashed"
                }
            },
            formatter: (params) => {
                const d = params[0].data;
                return (
                    `<b style="color:${style.colors[players.indexOf(d.player)]}">Draft ${d.x}, ` +
                    `${d.player}</b><br/>` +
                    `Pack ${d.pack}, Pick ${d.y}<br/>` +
                    `${d.run ? "Run": "Not Run"}<br/>` +
                    `Rank: ${d.rank}<br/>` +
                    `Deck Name: ${d.deck_name}`);
            }
        },
        grid:[
            {
                containLabel: true,
                left: "5%", top: "10%",
                width: "70%", height: "80%",
            },
        ],
        series: series.concat(wrSeries).concat(pieSeries),
    };
}

