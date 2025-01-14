function showInfo(library) {
    const details = {
        pygame: {
            info: "pygame is a cross-platform set of Python modules designed for writing video games. It includes computer graphics and sound libraries.",
            url: "https://www.pygame.org/tags/pygame",
        },
        heapq: {
            info: "heapq is a library that provides a heap queue algorithm, also known as the priority queue algorithm.",
            url: "https://docs.python.org/3/library/heapq.html",
        },
        random: {
            info: "The random module in Python generates pseudo-random numbers for random sampling, shuffling, and other operations.",
            url: "https://docs.python.org/3/library/random.html",
        },
        time: {
            info: "The time module in Python provides various time-related functions, such as tracking time or delaying execution.",
            url: "https://docs.python.org/3/library/time.html",
        },
    };

    const libraryDetails = details[library];
    if (libraryDetails) {
        const userChoice = confirm(
            `${libraryDetails.info}\n\nClick OK to open more details.`
        );
        if (userChoice) {
            window.open(libraryDetails.url, "_blank");
        }
    } else {
        alert("No details available for this library.");
    }
}
