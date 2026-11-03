const API_BASE_URL =
    "http://localhost:5001";


async function getHealthStatus() {

    try {

        const response =
            await fetch(
                `${API_BASE_URL}/health`
            );

        const data =
            await response.json();

        console.log(data);

        return data;

    } catch (error) {

        console.error(error);
    }
}


async function runSolver(solverName) {

    try {

        const response =
            await fetch(
                `${API_BASE_URL}/solver/run`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        solver: solverName
                    })
                }
            );

        const data =
            await response.json();

        return data;

    } catch (error) {

        console.error(error);
    }
}