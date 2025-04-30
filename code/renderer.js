const { exec } = require("child_process");
const path = require("path");
const fs = require("fs");

function loadTeams() {
  exec("python get_teams.py", (error, stdout, stderr) => {
    if (error) {
      console.error(`Error executing Python script: ${error.message}`);
      return;
    }
    if (stderr) {
      console.error(`stderr: ${stderr}`);
      return;
    }
    const teams = JSON.parse(stdout);
    const teamsList = document.getElementById("teams-list");
    teamsList.innerHTML = "";

    const headerItem = document.createElement("li");
    headerItem.className = "list-group-item";
    headerItem.innerHTML = `
          <div class="team-list-header">
            <span class="team-position"><strong></strong></span>
            <span class="team-name"><strong>Squadre</strong></span>
            <span><strong>V</strong></span>
            <span><strong>N</strong></span>
            <span><strong>P</strong></span>
            <span><strong>Goal</strong></span>
            <span><strong>PTI</strong></span>
          </div>
        `;
    teamsList.appendChild(headerItem);

    teams.forEach((team) => {
      const positionClass = getPositionClass(team.position);
      const listItem = document.createElement("li");
      listItem.className = "list-group-item custom-team-list-item";
      listItem.innerHTML = `
            <div class="team-list-item">
              <span class="team-position">${positionClass}</span>
              <span class="team-name"><img src="data:image/png;base64,${team.logo}" alt="${team.name}" width="30" height="auto"> ${team.name}</span>
              <span>${team.wins}</span>
              <span>${team.draws}</span>
              <span>${team.losses}</span>
              <span>${team.goals_for}:${team.goals_against}</span>
              <span>${team.points}</span>
            </div>
          `;

      listItem.addEventListener("click", () => {
        const teamName = team.name;
        const teamLogo = `data:image/png;base64,${team.logo}`;

        // Imposta il nome della squadra e il logo nella sezione dei grafici
        const teamNameTextElement = document.getElementById("team-name-text");
        teamNameTextElement.textContent = teamName;

        const teamLogoElement = document.getElementById("team-logo");
        teamLogoElement.src = teamLogo;
        teamLogoElement.style.display = "inline";

        // Salva il nome della squadra come attributo data
        const teamNameContainer = document.getElementById("team-name");
        teamNameContainer.setAttribute("data-team-name", teamName);

        showChartsSection();
        loadRoster(team.name);
      });

      teamsList.appendChild(listItem);
    });
  });
}

function getPositionClass(position) {
  if (position <= 5) {
    return `<span class="team-position-text green">${position}</span>`;
  } else if (position <= 7) {
    return `<span class="team-position-text light-blue">${position}</span>`;
  } else if (position == 8) {
    return `<span class="team-position-text sky-blue">${position}</span>`;
  } else if (position >= 18) {
    return `<span class="team-position-text red">${position}</span>`;
  } else {
    return `<span class="team-position-text">${position}</span>`; 
  }
}

function generateRadarChart(playerId) {
  const outputFile = path
    .join(__dirname, "radar_chart.png")
    .replace(/\\/g, "/");
  const command = `python radar.py ${playerId} "${outputFile}"`;
  console.log(`Executing command: ${command}`);  
  exec(command, (error, stdout, stderr) => {
    if (error) {
      console.error(`Error executing Python script: ${error.message}`);
      return;
    }
    if (stderr) {
      console.error(`stderr: ${stderr}`);
      return;
    }
    console.log(`Python stdout: ${stdout}`);
    fs.access(outputFile, fs.constants.F_OK, (err) => {
      if (err) {
        console.error(`File not found: ${outputFile}`);
        return;
      }
      const img = document.getElementById("radar-chart-img");
      img.src = `${outputFile}?t=${new Date().getTime()}`;  
      img.style.display = "block";
    });
  });
}

function generatePlayerHeatmap(gameId, playerId, playerName) {
  const outputFile = path
    .join(__dirname, "player_heatmap.png")
    .replace(/\\/g, "/");
  const command = `python heatmap.py ${gameId} ${playerId} "${playerName}" "${outputFile}"`;
  console.log(`Executing command: ${command}`);  

  exec(command, (error, stdout, stderr) => {
    if (error) {
      console.error(`Error executing Python script: ${error.message}`);
      return;
    }
    if (stderr) {
      console.error(`stderr: ${stderr}`);
      return;
    }
    console.log(`Python stdout: ${stdout}`);

    fs.access(outputFile, fs.constants.F_OK, (err) => {
      if (err) {
        console.error(`File not found: ${outputFile}`);
        return;
      }

      console.log(`File found: ${outputFile}`);
      const img = document.getElementById("heatmap-img");
      img.src = `${outputFile}?t=${new Date().getTime()}`;  
      img.style.display = "block";

      const playerNameElement = document.getElementById(
        "heatmap-player-name-text"
      );
      playerNameElement.textContent = playerName;

      const heatmapSection = document.getElementById("heatmap-section");
      heatmapSection.style.display = "block";

      const formationSection = document.getElementById("formation-section");
      if (formationSection) {
        formationSection.style.display = "none";
      }

      console.log("Heatmap image displayed.");
    });
  });
}

// Aggiunge un event listener per i clic dei giocatori nell'elenco della formazione
document
  .getElementById("formation-section")
  .addEventListener("click", (event) => {
    if (event.target && event.target.nodeName === "LI") {
      const playerName = event.target.textContent;
      const playerId = event.target.dataset.playerId;
      const gameId = event.target.dataset.gameId;
      console.log(
        `Player clicked: ${playerName}, playerId: ${playerId}, gameId: ${gameId}`
      );
      generatePlayerHeatmap(gameId, playerId, playerName);
    }
  });

function showChartsSection() {
  document.getElementById("teams-section").style.display = "none";
  document.getElementById("charts-section").style.display = "block";
  document.getElementById("matches-list").innerHTML = "";  
  document.getElementById("matches-section").style.display = "none";  
  document.getElementById("roster-section").style.display = "block";  
  document.getElementById("player-details-section").style.display = "none";  
  hideClearInterfaceButton();
}

function showTeamsSection() {
  const teamsSection = document.getElementById("teams-section");
  const chartsSection = document.getElementById("charts-section");
  if (teamsSection && chartsSection) {
    teamsSection.style.display = "block";
    chartsSection.style.display = "none";
  } else {
    if (!teamsSection) {
      console.error("Element with ID 'teams-section' not found");
    }
    if (!chartsSection) {
      console.error("Element with ID 'charts-section' not found");
    }
  }
}

function showMatchDetailsSection() {
  document.getElementById("charts-section").style.display = "none";
  document.getElementById("match-details-section").style.display = "block";
  showClearInterfaceButton();
}

function showMatchesSection() {
  document.getElementById("charts-section").style.display = "block";
  document.getElementById("match-details-section").style.display = "none";
  document.getElementById("roster-section").style.display = "none"; 
  document.getElementById("player-details-section").style.display = "none";
  document.getElementById("formation-section").style.display = "none"; 
  document.getElementById("matches-section").style.display = "block"; 

  const matchDetailsSection = document.getElementById("match-details-section");
  const formationContainers = matchDetailsSection.querySelectorAll(
    ".formation-container, .match-summary-container"
  );
  formationContainers.forEach((container) => container.remove());

  hideClearInterfaceButton();
}

function showRosterSection() {
  const chartsSection = document.getElementById("charts-section");
  const playerDetailsSection = document.getElementById(
    "player-details-section"
  );
  const rosterSection = document.getElementById("roster-section");
  if (chartsSection && playerDetailsSection && rosterSection) {
    chartsSection.style.display = "block";
    playerDetailsSection.style.display = "none";
    rosterSection.style.display = "block";
  } else {
    if (!chartsSection) {
      console.error("Element with ID 'charts-section' not found");
    }
    if (!playerDetailsSection) {
      console.error("Element with ID 'player-details-section' not found");
    }
    if (!rosterSection) {
      console.error("Element with ID 'roster-section' not found");
    }
  }
}

function showPlayerDetailsSection() {
  document.getElementById("charts-section").style.display = "none";
  document.getElementById("player-details-section").style.display = "block";
  showClearInterfaceButton();
}

function clearCharts() {
  const charts = [
    "shot-chart-img",
    "pass-flow-chart-img",
    "pass-plot-chart-img",
    "goal-chart-img",
    "heatmap-img",
  ];
  charts.forEach((chartId) => {
    const chart = document.getElementById(chartId);
    if (chart) {
      chart.src = "";
      chart.style.display = "none";
    }
  });
  document.getElementById("no-goals-message").style.display = "none";

  const formationContainers = document.querySelectorAll(
    ".formation-container, .match-summary-container"
  );
  formationContainers.forEach(
    (container) => (container.style.display = "none")
  );

  const heatmapSection = document.getElementById("heatmap-section");
  if (heatmapSection) {
    heatmapSection.style.display = "none";
  }
}

// Funzione per generare la formazione
function generateFormation(gameId, team1Id, team2Id) {
  clearCharts();
  const command = `python titolari_sub.py ${gameId} ${team1Id} ${team2Id}`;
  console.log(`Executing command: ${command}`);
  exec(command, (error, stdout, stderr) => {
    if (error) {
      console.error(`Error executing Python script: ${error.message}`);
      return;
    }
    if (stderr) {
      console.error(`stderr: ${stderr}`);
      return;
    }
    console.log(`Python stdout: ${stdout}`);

    let formationData;
    try {
      formationData = JSON.parse(stdout);
    } catch (e) {
      console.error(`Error parsing JSON: ${e.message}`);
      return;
    }

    const {
      home_team_name,
      away_team_name,
      home_team_coach_name,
      away_team_coach_name,
      homeTeamPlayers,
      homeTeamPlayerIds,
      homeTeamSubs,
      homeTeamSubIds,
      homeTeamSubDetails,
      awayTeamPlayers,
      awayTeamPlayerIds,
      awayTeamSubs,
      awayTeamSubIds,
      awayTeamSubDetails,
      label,
      gameweek,
      formatted_date,
      team1_scoreHT,
      team2_scoreHT,
      team1_side,
      team2_side,
    } = formationData;

    const matchDetailsSection = document.getElementById(
      "match-details-section"
    );

    // Cancella le formazioni precedenti e il riepilogo della partita
    const formationContainers = matchDetailsSection.querySelectorAll(
      ".formation-container, .match-summary-container"
    );
    formationContainers.forEach((container) => container.remove());

    // Determina il risultato del primo tempo in base alle squadre
    let halftimeResult = "";
    if (team1_side === "home") {
      halftimeResult = `${team1_scoreHT}-${team2_scoreHT}`;
    } else {
      halftimeResult = `${team2_scoreHT}-${team1_scoreHT}`;
    }

    // Riepilogo della partita
    const matchSummaryContainer = document.createElement("div");
    matchSummaryContainer.className = "match-summary-container";
    matchSummaryContainer.innerHTML = `
      <h2>${label}</h2>
      <p>${gameweek}° giornata - ${formatted_date}</p>
      <p>Allenatore ${home_team_name}: ${home_team_coach_name}</p>
      <p>Allenatore ${away_team_name}: ${away_team_coach_name}</p>
      <p>Risultato primo tempo: ${halftimeResult}</p>
    `;

    const buttonsContainer = document.querySelector(
      "#match-details-section .btn-group"
    );
    buttonsContainer.insertAdjacentElement("afterend", matchSummaryContainer);

    const formationContainer = document.createElement("div");
    formationContainer.className = "formation-container";
    formationContainer.innerHTML = `
      <div class="team-formation">
        <h3>${home_team_name}</h3>
        <ul id="home-team-starters" class="list-group formation-list"></ul>
        <h4>Sostituti</h4>
        <ul id="home-team-subs" class="list-group formation-list"></ul>
      </div>
      <div class="team-formation">
        <h3>${away_team_name}</h3>
        <ul id="away-team-starters" class="list-group formation-list"></ul>
        <h4>Sostituti</h4>
        <ul id="away-team-subs" class="list-group formation-list"></ul>
      </div>
    `;
    matchDetailsSection.appendChild(formationContainer);

    const homeTeamStartersList = document.getElementById("home-team-starters");
    homeTeamPlayers.forEach((player, index) => {
      const listItem = document.createElement("li");
      listItem.className = "list-group-item matches-item formation-item";
      listItem.style.width = "100%"; 
      listItem.textContent = `${player[0]} (${player[1]})`;
      listItem.dataset.playerId = homeTeamPlayerIds[index];
      listItem.dataset.gameId = gameId;

      if (player[1] !== "Portiere") { // Controlla se il giocatore non è un portiere
        listItem.addEventListener("click", () => {
          generatePlayerHeatmap(gameId, homeTeamPlayerIds[index], player[0]);
        });
      } else {
        listItem.style.cursor = "default";
      }

      homeTeamStartersList.appendChild(listItem);
    });

    const homeTeamSubsList = document.getElementById("home-team-subs");
    homeTeamSubs.forEach((sub, index) => {
      const listItem = document.createElement("li");
      listItem.className = "list-group-item matches-item formation-item";
      listItem.style.width = "100%";  
      listItem.textContent = `${sub[0]} (${sub[1]}) - Sostituisce ${homeTeamSubDetails[index].playerOutName} al minuto ${homeTeamSubDetails[index].minute}`;
      listItem.dataset.playerId = homeTeamSubIds[index];
      listItem.dataset.gameId = gameId;

      if (sub[1] !== "Portiere") {  // Controlla se il giocatore non è un portiere
        listItem.addEventListener("click", () => {
          generatePlayerHeatmap(gameId, homeTeamSubIds[index], sub[0]);
        });
      } else {
        listItem.style.cursor = "default";
      }

      homeTeamSubsList.appendChild(listItem);
    });

    const awayTeamStartersList = document.getElementById("away-team-starters");
    awayTeamPlayers.forEach((player, index) => {
      const listItem = document.createElement("li");
      listItem.className = "list-group-item matches-item formation-item";
      listItem.style.width = "100%";  
      listItem.textContent = `${player[0]} (${player[1]})`;
      listItem.dataset.playerId = awayTeamPlayerIds[index];
      listItem.dataset.gameId = gameId;

      if (player[1] !== "Portiere") {  // Controlla se il giocatore non è un portiere
        listItem.addEventListener("click", () => {
          generatePlayerHeatmap(gameId, awayTeamPlayerIds[index], player[0]);
        });
      } else {
        listItem.style.cursor = "default";
      }

      awayTeamStartersList.appendChild(listItem);
    });

    const awayTeamSubsList = document.getElementById("away-team-subs");
    awayTeamSubs.forEach((sub, index) => {
      const listItem = document.createElement("li");
      listItem.className = "list-group-item matches-item formation-item";
      listItem.style.width = "100%";  
      listItem.textContent = `${sub[0]} (${sub[1]}) - Sostituisce ${awayTeamSubDetails[index].playerOutName} al minuto ${awayTeamSubDetails[index].minute}`;
      listItem.dataset.playerId = awayTeamSubIds[index];
      listItem.dataset.gameId = gameId;

      if (sub[1] !== "Portiere") {  // Controlla se il giocatore non è un portiere
        listItem.addEventListener("click", () => {
          generatePlayerHeatmap(gameId, awayTeamSubIds[index], sub[0]);
        });
      } else {
        listItem.style.cursor = "default";
      }

      awayTeamSubsList.appendChild(listItem);
    });

    showMatchDetailsSection();
  });
}

function loadMatches(teamName) {
  const getMatchesScript = path
    .join(__dirname, "get_matches.py")
    .replace(/\\/g, "/");
  const command = `python ${getMatchesScript} "${teamName}"`;
  console.log(`Executing command: ${command}`);  

  document.getElementById("matches-loader").style.display = "flex";
  document.getElementById("matches-section").style.display = "none";
  document.getElementById("roster-section").style.display = "none"; 

  exec(command, (error, stdout, stderr) => {
    if (error) {
      console.error(`Error executing Python script: ${error.message}`);
      return;
    }
    if (stderr) {
      console.error(`stderr: ${stderr}`);
      return;
    }
    const matches = JSON.parse(stdout);
    const matchesList = document.getElementById("matches-list");
    matchesList.innerHTML = ""; 

    const headerItem = document.createElement("li");
    headerItem.className = "list-group-item";
    headerItem.innerHTML = `
      <div class="matches-header">
        <span><strong>Giornata</strong></span>
        <span><strong>Squadre</strong></span>
        <span><strong>Risultato</strong></span>
      </div>
    `;
    matchesList.appendChild(headerItem);

    matches.forEach((match) => {
      const listItem = document.createElement("li");
      listItem.className = "list-group-item matches-item"; 

      const gameweek = match.gameweek !== undefined ? match.gameweek : "N/A";
      const squadre = match.squadre !== undefined ? match.squadre : "N/A";
      const risultato = match.risultato !== undefined ? match.risultato : "N/A";
      const wyId = match.wyId !== undefined ? match.wyId : "N/A"; 

      listItem.innerHTML = `
        <span>${gameweek}</span>
        <span>${squadre}</span>
        <span>${risultato}</span>
      `;
      listItem.dataset.gameId = wyId;
      listItem.addEventListener("click", () => {
        const gameId = listItem.dataset.gameId;
        console.log(`Match clicked, gameId: ${gameId}`);

        if (gameId && gameId !== "N/A") {
          exec(
            `python get_match_details.py ${gameId}`,
            (error, stdout, stderr) => {
              if (error) {
                console.error(
                  `Error executing Python script: ${error.message}`
                );
                return;
              }
              if (stderr) {
                console.error(`stderr: ${stderr}`);
                return;
              }
              const matchDetails = JSON.parse(stdout);
              const team1Id = matchDetails.team1Id;
              const team2Id = matchDetails.team2Id;
              const team1Name = matchDetails.team1Name;
              const team2Name = matchDetails.team2Name;
              const homeTeamName = matchDetails.homeTeamName;
              const awayTeamName = matchDetails.awayTeamName;

              const matchDetailsSection = document.getElementById(
                "match-details-section"
              );
              matchDetailsSection.dataset.gameId = gameId;
              matchDetailsSection.dataset.team1Id = team1Id;
              matchDetailsSection.dataset.team2Id = team2Id;
              matchDetailsSection.dataset.team1Name = team1Name;
              matchDetailsSection.dataset.team2Name = team2Name;

              const passFlowButtonTeam1 = document.getElementById(
                "generate-pass-flow-team1"
              );
              passFlowButtonTeam1.textContent = `${team1Name} flusso di passaggi`;
              passFlowButtonTeam1.onclick = () => {
                console.log(
                  `Generating pass flow chart for ${team1Name} (${team1Id})`
                );
                generatePassFlowChart(gameId, team1Id, team1Name);
              };

              const passFlowButtonTeam2 = document.getElementById(
                "generate-pass-flow-team2"
              );
              passFlowButtonTeam2.textContent = `${team2Name} flusso di passaggi`;
              passFlowButtonTeam2.onclick = () => {
                console.log(
                  `Generating pass flow chart for ${team2Name} (${team2Id})`
                );
                generatePassFlowChart(gameId, team2Id, team2Name);
              };

              const passPlotButtonTeam1 = document.getElementById(
                "generate-pass-plot-team1"
              );
              passPlotButtonTeam1.textContent = `${team1Name} grafico passaggi`;
              passPlotButtonTeam1.onclick = () => {
                console.log(
                  `Generating pass plot for ${team1Name} (${team1Id})`
                );
                generatePassPlot(gameId, team1Id, team1Name);
              };

              const passPlotButtonTeam2 = document.getElementById(
                "generate-pass-plot-team2"
              );
              passPlotButtonTeam2.textContent = `${team2Name} grafico passaggi`;
              passPlotButtonTeam2.onclick = () => {
                console.log(
                  `Generating pass plot for ${team2Name} (${team2Id})`
                );
                generatePassPlot(gameId, team2Id, team2Name);
              };

              const shotChartButton = document.getElementById(
                "generate-shot-chart"
              );
              shotChartButton.onclick = () => {
                console.log(`Generating shot chart for game ${gameId}`);
                generateShotChart(
                  gameId,
                  team1Id,
                  team2Id,
                  team1Name,
                  team2Name
                );
              };

              const goalChartButton = document.getElementById(
                "generate-goal-chart"
              );
              goalChartButton.onclick = () => {
                console.log(`Generating goal chart for game ${gameId}`);
                generateGoalChart(
                  gameId,
                  team1Id,
                  team2Id,
                  team1Name,
                  team2Name
                );
              };

              const formationButton =
                document.getElementById("generate-formation");
              formationButton.onclick = () => {
                console.log(`Generating formation for game ${gameId}`);
                generateFormation(gameId, team1Id, team2Id);
              };

              // Imposta i nomi delle squadre di casa e in trasferta
              document.getElementById(
                "home-team-name"
              ).textContent = `Squadra casa: ${homeTeamName}`;
              document.getElementById(
                "away-team-name"
              ).textContent = `Squadra ospite: ${awayTeamName}`;

              showMatchDetailsSection();
              generateFormation(gameId, team1Id, team2Id);
            }
          );
        } else {
          console.error("gameId is undefined");
        }
      });

      matchesList.appendChild(listItem);
    });
    document.getElementById("matches-loader").style.display = "none";
    document.getElementById("matches-section").style.display = "block"; 
  });
}

function hideSummaryLoader() {
  console.log("hideSummaryLoader called");
  const loader = document.getElementById("summary-loader");
  if (loader) {
    loader.style.display = "none";
    console.log("Summary loader hidden");
  } else {
    console.log("Summary loader element not found");
  }
}

function generateVisualization2() {
  const { exec } = require("child_process");
  const path = require("path");

  const outputFilePath = path.join(__dirname, "summary_chart.png");
  const scriptPath = path.join(__dirname, "generate_visualization_2.py");

  // Nascondi la sezione delle squadre e il titolo
  document.getElementById("teams-section").style.display = "none";
  document.querySelector("h1.text-center").style.display = "none";
  document.getElementById("generate-chart-2").style.display = "none";

  showSummaryLoader();

  exec(`python ${scriptPath} ${outputFilePath}`, (error, stdout, stderr) => {
    hideSummaryLoader();

    if (error) {
      console.error(`exec error: ${error.message}`);
      return;
    }
    console.log(`stdout: ${stdout}`);
    console.error(`stderr: ${stderr}`);

    // Verifica che il file esista prima di tentare di mostrarlo
    const fs = require("fs");
    fs.access(outputFilePath, fs.constants.F_OK, (err) => {
      if (err) {
        console.error(`File not found: ${outputFilePath}`);
        return;
      }

      const summaryChartImg = document.getElementById("summary-chart-img");
      summaryChartImg.src = `${outputFilePath}?t=${new Date().getTime()}`;  
      summaryChartImg.style.display = "block";

      document.getElementById("summary-chart-section").style.display = "block";
    });
  });
}

document.getElementById("generate-chart-2").addEventListener("click", () => {
  console.log("Button 2 clicked");
  generateVisualization2();
});

document
  .getElementById("back-to-teams-summary")
  .addEventListener("click", () => {
    document.getElementById("summary-chart-section").style.display = "none";
    document.getElementById("teams-section").style.display = "block";
    document.getElementById("generate-chart-2").style.display = "block"; 
    document.querySelector("h1.text-center").style.display = "block"; 
  });

const clearButton = document.getElementById("clear-interface");
if (clearButton) {
  clearButton.addEventListener("click", () => {
    console.log("Clear button clicked");
    const img = document.getElementById("chart-img");
    img.src = "";
    img.style.display = "none";
    const img2 = document.getElementById("chart-img-2");
    img2.src = "";
    img2.style.display = "none";
    const shotImg = document.getElementById("shot-chart-img");
    shotImg.src = "";
    shotImg.style.display = "none";
    const passFlowImg = document.getElementById("pass-flow-chart-img");
    passFlowImg.src = "";
    passFlowImg.style.display = "none";
    const passPlotImg = document.getElementById("pass-plot-chart-img");
    passPlotImg.src = "";
    passPlotImg.style.display = "none";
    const goalImg = document.getElementById("goal-chart-img");
    goalImg.src = "";
    goalImg.style.display = "none";
    document.getElementById("matches-list").innerHTML = "";
    document.getElementById("matches-section").style.display = "none";
    document.getElementById("roster-list").innerHTML = "";
    document.getElementById("roster-section").style.display = "none";
    document.getElementById("player-details-section").style.display = "none";
    document.getElementById("formation-output").innerHTML = "";
    document.getElementById("formation-output").style.display = "none";
    document.getElementById("no-goals-message").style.display = "none";
  });
}

function hideClearInterfaceButton() {
  const clearButton = document.getElementById("clear-interface");
  if (clearButton) {
    clearButton.style.display = "none";
  }
}

function showClearInterfaceButton() {
  const clearButton = document.getElementById("clear-interface");
  if (clearButton) {
    clearButton.style.display = "inline-block";
  }
}

document.getElementById("back-to-teams").addEventListener("click", () => {
  console.log("Back to Teams button clicked");
  clearRoster();
  showTeamsSection();
});

function clearRoster() {
  const rosterList = document.getElementById("roster-list");
  if (rosterList) {
    rosterList.innerHTML = ""; 
  } else {
    console.error("Element with ID 'roster-list' not found");
    return;
  }
  const rosterHeader = document.getElementById("roster-header");
  if (rosterHeader) {
    rosterHeader.style.display = "none";
  } else {
    console.error("Element with ID 'roster-header' not found");
    return;
  }
}

document.getElementById("back-to-matches").addEventListener("click", () => {
  clearCharts(); 
  showMatchesSection();
  document.getElementById("shot-chart-img").style.display = "none";
  document.getElementById("shot-chart-img").src = "";
  document.getElementById("pass-flow-chart-img").style.display = "none";
  document.getElementById("pass-flow-chart-img").src = "";
  document.getElementById("pass-plot-chart-img").style.display = "none";
  document.getElementById("pass-plot-chart-img").src = "";
  document.getElementById("goal-chart-img").style.display = "none";
  document.getElementById("goal-chart-img").src = "";
  document.getElementById("no-goals-message").style.display = "none";
  document.getElementById("formation-output").style.display = "none"; 
  document.getElementById("formation-output").innerHTML = ""; 

  const shotChartContainer = document.getElementById("shot-chart-container");
  shotChartContainer.style.display = "none";
  const img = document.getElementById("shot-chart-img");
  img.src = "";
  img.style.display = "none";

  const formationContainers = document.querySelectorAll(
    ".formation-container, .match-summary-container"
  );
  formationContainers.forEach(
    (container) => (container.style.display = "block")
  );
});

document.getElementById("back-to-roster").addEventListener("click", () => {
  showRosterSection();
  document.getElementById("player-details-section").style.display = "none";
  document.getElementById("radar-chart-img").style.display = "none";
  document.getElementById("radar-chart-img").src = "";
  document.getElementById("chart-img").style.display = "none";
  document.getElementById("chart-img").src = "";
  enableButtons();
});

document.getElementById("show-matches").addEventListener("click", () => {
  const teamName = document
    .getElementById("team-name")
    .getAttribute("data-team-name");
  console.log("Show Matches button clicked, team:", teamName);
  loadMatches(teamName);
});

document.getElementById("show-roster").addEventListener("click", () => {
  const teamName = document
    .getElementById("team-name")
    .getAttribute("data-team-name");
  console.log("Show Roster button clicked, team:", teamName);
  loadRoster(teamName);
});

function decodeUnicode(str) {
  return str.replace(/\\u[\dA-Fa-f]{4}/g, function (match) {
    return String.fromCharCode(parseInt(match.replace(/\\u/g, ""), 16));
  });
}

function loadRoster(teamName) {
  const getRosterScript = path
    .join(__dirname, "get_roster.py")
    .replace(/\\/g, "/");
  const command = `python ${getRosterScript} "${teamName}"`;
  console.log(`Executing command: ${command}`);  

  // Cancella l'elenco precedente e nasconde la sezione dell'elenco e il pulsante Indietro
  const rosterList = document.getElementById("roster-list");
  if (rosterList) {
    rosterList.innerHTML = ""; 
  } else {
    console.error("Element with ID 'roster-list' not found");
    return;
  }

  const rosterSection = document.getElementById("roster-section");
  if (rosterSection) {
    rosterSection.style.display = "none";
  } else {
    console.error("Element with ID 'roster-section' not found");
    return;
  }

  const matchesSection = document.getElementById("matches-section");
  if (matchesSection) {
    matchesSection.style.display = "none"; 
  } else {
    console.error("Element with ID 'matches-section' not found");
    return;
  }

  const rosterLoader = document.getElementById("roster-loader");
  if (rosterLoader) {
    rosterLoader.style.display = "flex";
  } else {
    console.error("Element with ID 'roster-loader' not found");
    return;
  }

  exec(command, (error, stdout, stderr) => {
    if (error) {
      console.error(`Error executing Python script: ${error.message}`);
      return;
    }
    if (stderr) {
      console.error(`stderr: ${stderr}`);
      return;
    }
    rosterList.innerHTML = "";

    const headerItem = document.createElement("li");
    headerItem.className = "list-group-item";
    headerItem.innerHTML = `
      <div class="roster-header">
        <span><strong>Nome</strong></span>
        <span><strong>Ruolo</strong></span>
        <span><strong>Minuti giocati</strong></span>
        <span><strong>Gol</strong></span>
      </div>
    `;
    rosterList.appendChild(headerItem);

    const players = JSON.parse(stdout).map((player) => {
      return {
        name: decodeUnicode(player.name),
        wyid: player.wyId,
        role: player.role,
        minutes: player.minutes,
        goals: player.goals,
      };
    });

    const rosterHeader = document.getElementById("roster-header");
    if (players.length > 0) {
      if (rosterHeader) {
        rosterHeader.style.display = "block"; 
      } else {
        console.error("Element with ID 'roster-header' not found");
        return;
      }
    }

    players.forEach((player) => {
      const listItem = document.createElement("li");
      listItem.className = "list-group-item list-group-item-action";
      listItem.innerHTML = `
        <div class="roster-item">
          <span>${player.name}</span>
          <span>${player.role}</span>
          <span>${player.minutes}</span>
          <span>${player.goals > 0 ? player.goals : ""}</span>
        </div>
      `;
      listItem.dataset.playerId = player.wyid;
      listItem.dataset.playerName = player.name;
      listItem.addEventListener("click", () => {
        const playerNameElement = document.getElementById("player-name");
        if (playerNameElement) {
          playerNameElement.textContent = `${player.name}`;
          playerNameElement.dataset.playerId = player.wyid;
          playerNameElement.dataset.playerName = player.name;
        } else {
          console.error("Element with ID 'player-name' not found");
          return;
        }
        showPlayerDetailsSection();

        // Mostra il loader e genera automaticamente il radar chart
        showPlayerLoader();
        generateRadarChart(player.wyid);

        // Imposta il pulsante Genera grafico con il wyId e il nome del giocatore selezionato
        const generateChartButton = document.getElementById("generate-chart-1");
        if (generateChartButton) {
          generateChartButton.onclick = () => {
            const playerId = playerNameElement.dataset.playerId;
            const playerName = playerNameElement.dataset.playerName;
            console.log(
              `Generating chart for player ID: ${playerId}, Name: ${playerName}`
            );
            generateVisualization(playerId, playerName);
          };
        } else {
          console.error("Element with ID 'generate-chart-1' not found");
        }
      });

      rosterList.appendChild(listItem);
    });

    rosterLoader.style.display = "none";
    rosterSection.style.display = "block";
  });
}

function showPlayerLoader() {
  const loader = document.getElementById("player-loader");
  if (loader) {
    loader.style.display = "flex";
  }
}

function showSummaryLoader() {
  console.log("showSummaryLoader called");
  const loader = document.getElementById("summary-loader");
  if (loader) {
    loader.style.display = "flex";
    console.log("Summary loader displayed");
  } else {
    console.log("Summary loader element not found");
  }
}

function hideSummaryLoader() {
  console.log("hideSummaryLoader called");
  const loader = document.getElementById("summary-loader");
  if (loader) {
    loader.style.display = "none";
    console.log("Summary loader hidden");
  } else {
    console.log("Summary loader element not found");
  }
}

function showMatchLoader() {
  document.getElementById("match-loader").style.display = "flex";
}

function hideMatchLoader() {
  document.getElementById("match-loader").style.display = "none";
}

function showLoader() {
  const loader = document.getElementById("summary-loader");
  if (loader) {
    loader.style.display = "flex";
  }
}

function hideLoader() {
  const loader = document.getElementById("summary-loader");
  if (loader) {
    loader.style.display = "none";
  }
}

let isVisualizationGenerated = false;
let isRadarChartGenerated = false;

function checkAndDisableButtons() {
  const generateChartButton = document.getElementById("generate-chart-1");
  const generateRadarButton = document.getElementById("generate-radar-chart");

  if (isVisualizationGenerated && isRadarChartGenerated) {
    if (generateChartButton) {
      generateChartButton.disabled = true;
    }
    if (generateRadarButton) {
      generateRadarButton.disabled = true;
    }
  }
}

function enableButtons() {
  const generateChartButton = document.getElementById("generate-chart-1");
  const generateRadarButton = document.getElementById("generate-radar-chart");

  if (generateChartButton) {
    generateChartButton.disabled = false;
  }
  if (generateRadarButton) {
    generateRadarButton.disabled = false;
  }
  isVisualizationGenerated = false;
  isRadarChartGenerated = false;
}

function generateVisualization(playerId) {
  const outputFile = path
    .join(__dirname, "visualization1.png")
    .replace(/\\/g, "/");
  const generateVisualizationScript = path
    .join(__dirname, "generate_visualization.py")
    .replace(/\\/g, "/");
  const command = `python ${generateVisualizationScript} "${outputFile}" "${playerId}"`;
  console.log(`Executing command: ${command}`);  

  showLoader();
  exec(command, (error, stdout, stderr) => {
    hideLoader();

    if (error) {
      console.error(`Error executing Python script: ${error.message}`);
      return;
    }
    if (stderr) {
      console.error(`stderr: ${stderr}`);
      return;
    }
    console.log(`Python stdout: ${stdout}`);
    const img = document.getElementById("chart-img");
    console.log(`Updating img.src to: ${outputFile}`);
    img.src = `${outputFile}?t=${new Date().getTime()}`;  
    img.style.display = "block";

    isVisualizationGenerated = true;
    checkAndDisableButtons();
  });
}

function decodeUnicode(str) {
  return str.replace(/\\u[\dA-F]{4}/gi, function (match) {
    return String.fromCharCode(parseInt(match.replace(/\\u/g, ""), 16));
  });
}

document.getElementById("generate-chart-1").addEventListener("click", () => {
  const playerId = document.getElementById("player-name").dataset.playerId;
  generateVisualization(playerId);
});

function generateShotChart(gameId, team1Id, team2Id, team1Name, team2Name) {
  clearCharts();  
  showMatchLoader();
  const outputFile = path.join(__dirname, "shot_chart.png").replace(/\\/g, "/");
  const generateShotChartScript = path
    .join(__dirname, "generate_shot_chart.py")
    .replace(/\\/g, "/");
  const command = `python ${generateShotChartScript} ${gameId} ${team1Id} ${team2Id} "${team1Name}" "${team2Name}" "${outputFile}"`;
  console.log(`Executing command: ${command}`);

  exec(command, (error, stdout, stderr) => {
    hideMatchLoader();
    if (error) {
      console.error(`Error executing Python script: ${error.message}`);
      return;
    }
    if (stderr) {
      console.error(`stderr: ${stderr}`);
      return;
    }
    console.log(`Python stdout: ${stdout}`);
    fs.access(outputFile, fs.constants.F_OK, (err) => {
      if (err) {
        console.error(`File not found: ${outputFile}`);
        return;
      }
      const img = document.getElementById("shot-chart-img");
      console.log(`Updating img.src to: ${outputFile}`);
      img.src = `${outputFile}?t=${new Date().getTime()}`;
      img.style.display = "block";
      const shotChartContainer = document.getElementById(
        "shot-chart-container"
      );
      shotChartContainer.style.display = "block";
    });
  });
}

document.getElementById("generate-shot-chart").addEventListener("click", () => {
  const gameIdElement = document.querySelector("[data-game-id]");
  const team1IdElement = document.querySelector("[data-team1-id]");
  const team2IdElement = document.querySelector("[data-team2-id]");
  const team1NameElement = document.querySelector("[data-team1-name]");
  const team2NameElement = document.querySelector("[data-team2-name]");

  if (
    !gameIdElement ||
    !team1IdElement ||
    !team2IdElement ||
    !team1NameElement ||
    !team2NameElement
  ) {
    console.error("One or more required data attributes are missing.");
    return;
  }

  const gameId = gameIdElement.dataset.gameId;
  const team1Id = team1IdElement.dataset.team1Id;
  const team2Id = team2IdElement.dataset.team2Id;
  const team1Name = team1NameElement.dataset.team1Name;
  const team2Name = team2NameElement.dataset.team2Name;

  generateShotChart(gameId, team1Id, team2Id, team1Name, team2Name);
});

function generateRadarChart(playerId) {
  const outputFile = path
    .join(__dirname, "radar_chart.png")
    .replace(/\\/g, "/");
  const command = `python radar.py ${playerId} "${outputFile}"`;
  console.log(`Executing command: ${command}`);  

  showLoader();

  exec(command, (error, stdout, stderr) => {
    hideLoader();

    if (error) {
      console.error(`Error executing Python script: ${error.message}`);
      return;
    }
    if (stderr) {
      console.error(`stderr: ${stderr}`);
      return;
    }
    console.log(`Python stdout: ${stdout}`);
    const img = document.getElementById("radar-chart-img");
    console.log(`Updating img.src to: ${outputFile}`);
    img.src = `${outputFile}?t=${new Date().getTime()}`;  
    img.style.display = "block";

    isRadarChartGenerated = true;
    checkAndDisableButtons();
  });
}

function generatePassFlowChart(gameId, teamId, teamName) {
  clearCharts();  
  showMatchLoader();
  if (!teamId) {
    console.error("Team ID is undefined");
    return;
  }
  const outputFile = path.join(__dirname, "pass_flow.png").replace(/\\/g, "/");
  const generatePassFlowScript = path
    .join(__dirname, "flussopassaggi.py")
    .replace(/\\/g, "/");
  const command = `python ${generatePassFlowScript} ${gameId} ${teamId} "${teamName}" "${outputFile}"`;
  console.log(`Executing command: ${command}`);

  exec(command, (error, stdout, stderr) => {
    hideMatchLoader();
    if (error) {
      console.error(`Error executing Python script: ${error.message}`);
      return;
    }
    if (stderr) {
      console.error(`stderr: ${stderr}`);
      return;
    }
    console.log(`Python stdout: ${stdout}`);
    fs.access(outputFile, fs.constants.F_OK, (err) => {
      if (err) {
        console.error(`File not found: ${outputFile}`);
        return;
      }
      const img = document.getElementById("pass-flow-chart-img");
      console.log(`Updating img.src to: ${outputFile}`);
      img.src = `${outputFile}?t=${new Date().getTime()}`;
      img.style.display = "block";
    });
  });
}

function generatePassPlot(gameId, teamId, teamName) {
  clearCharts();  
  showMatchLoader();
  if (!teamId) {
    console.error("Team ID is undefined");
    return;
  }
  const outputFile = path.join(__dirname, "pass_plot.png").replace(/\\/g, "/");
  const generatePassPlotScript = path
    .join(__dirname, "passplot.py")
    .replace(/\\/g, "/");
  const command = `python ${generatePassPlotScript} ${gameId} ${teamId} "${teamName}" "${outputFile}"`;
  console.log(`Executing command: ${command}`);

  exec(command, (error, stdout, stderr) => {
    hideMatchLoader();
    if (error) {
      console.error(`Error executing Python script: ${error.message}`);
      return;
    }
    if (stderr) {
      console.error(`stderr: ${stderr}`);
      return;
    }
    console.log(`Python stdout: ${stdout}`);
    fs.access(outputFile, fs.constants.F_OK, (err) => {
      if (err) {
        console.error(`File not found: ${outputFile}`);
        return;
      }
      const img = document.getElementById("pass-plot-chart-img");
      console.log(`Updating img.src to: ${outputFile}`);
      img.src = `${outputFile}?t=${new Date().getTime()}`;
      img.style.display = "block";
    });
  });
}

function generateGoalChart(gameId, team1Id, team2Id, team1Name, team2Name) {
  clearCharts();  
  showMatchLoader();
  const outputFile = path.join(__dirname, "goal_chart.png").replace(/\\/g, "/");
  const command = `python generate_goals.py ${gameId} ${team1Id} ${team2Id} "${team1Name}" "${team2Name}" "${outputFile}"`;
  console.log(`Executing command: ${command}`);

  exec(command, (error, stdout, stderr) => {
    hideMatchLoader();
    if (error) {
      console.error(`Error executing Python script: ${error.message}`);
      return;
    }
    if (stderr) {
      console.error(`stderr: ${stderr}`);
      return;
    }
    console.log(`Python stdout: ${stdout}`);
    fs.access(outputFile, fs.constants.F_OK, (err) => {
      if (err) {
        console.error(`File not found: ${outputFile}`);
        return;
      }
      const img = document.getElementById("goal-chart-img");
      console.log(`Updating img.src to: ${outputFile}`);
      img.src = `${outputFile}?t=${new Date().getTime()}`;
      img.style.display = "block";
      fs.readFile(outputFile, (err, data) => {
        if (err) {
          console.error(`Error reading file: ${err.message}`);
          return;
        }
        const imgTag = document.createElement("img");
        imgTag.src = `data:image/png;base64,${data.toString("base64")}`;
        imgTag.onload = () => {
          const canvas = document.createElement("canvas");
          canvas.width = imgTag.width;
          canvas.height = imgTag.height;
          const ctx = canvas.getContext("2d");
          ctx.drawImage(imgTag, 0, 0);
          const imgData = ctx.getImageData(0, 0, canvas.width, canvas.height);
          const isEmpty = !imgData.data.some((channel) => channel !== 255);
          if (isEmpty) {
            document.getElementById("goal-chart-img").style.display = "none";
            document.getElementById("no-goals-message").style.display = "block";
          } else {
            document.getElementById("goal-chart-img").style.display = "block";
            document.getElementById("no-goals-message").style.display = "none";
          }
        };
      });
    });
  });
}

window.onload = loadTeams;
