# DOOMHouse: When SQL Becomes a GPU

"You can't write a 3D game engine in SQL."

I must have heard that phrase... well, actually, I never heard it because nobody is crazy enough to try. But if they did, they'd be right. It's a terrible idea. SQL is for data, not for raycasting.

So naturally, I had to try it.

I've been spending my nights building **DOOMHouse**, a project that asks a simple, ridiculous question: Can we abuse ClickHouse's analytical power to render a Wolfenstein 3D-style game in real-time?

The answer is yes. But getting there? That was a journey.

## The Squad

I didn't write this code alone. In fact, I barely wrote the SQL myself. I acted more like a conductor for an orchestra of AI agents.

I used **Gemini 3.0 Pro** and **Flash** for the heavy lifting, **Opus 4.5** for the complex logic reasoning, and **ChatGPT 5.2** to handle the texture mapping mathematics.

The process wasn't just "generate code." It was deeply iterative. I'd get a query that worked, and then I'd ask the model: *"Okay, now optimize it."*

Then I'd take *that* result and feed it back: *"Optimize it again."*

We did this loop dozens of times. The SQL queries grew from simple selects into these massive, vectorized monsters that looked less like database queries and more like assembly language.

## Visual Debugging

Here's where it got weird.

Debugging SQL logic for 3D rendering is a nightmare. You can't just `console.log` a ray intersection. So I started doing something I call "Visual Debugging."

I would run the render, take a screenshot of the glitchy, broken wall, and feed that image back to the agent.

*"See this artifact on the left? The texture is shearing. Fix it."*

And it would. The model would look at the visual output of its own code, understand the mathematical error causing the visual glitch, and rewrite the SQL to correct it. That feedback loop—Code → Render → Screenshot → Agent → Code—felt like a glimpse into the future of programming.

## The Architecture

To make this actually run at a playable framerate, we couldn't just run one big query. We had to get creative.

The rendering pipeline is split into **4 parallel pipelines**.

1.  **Raycasting**: Calculating where the walls are.
2.  **Texture Mapping**: Figuring out which pixel of the texture goes where.
3.  **Shading/Lighting**: Applying distance-based fog and side-shading.
4.  **Post-Processing**: A SWAR-based smoothing filter to make it look less jagged.

All of this happens inside ClickHouse. The database isn't just storing the level data; it *is* the GPU.

## Breaking the Database

We pushed it too hard.

At one point, the SQL became so complex—so deeply nested with array operations and vectorized math—that it actually crashed ClickHouse.

I don't mean it timed out. I mean it broke the server.

It turned out we had uncovered an edge case in how ClickHouse handles extreme vectorization. The code I generated with the agents actually helped the ClickHouse team verify a solution for a bug they hadn't seen in the wild.

When your SQL is so intense it uncovers compiler bugs, you know you're onto something.

## What's Missing

It's not perfect.

Right now, I don't have analytics on the token usage it took to get here (it was... a lot). I also wish I had better logging of the "thinking" process the agents went through. Watching them reason through 3D math in a declarative language was fascinating, and I wish I had preserved more of that chain of thought.

## The Future

Building DOOMHouse changed how I look at coding.

We're moving into an era where we aren't just writing code; we're guiding intelligence to write code that is too complex for us to write by hand. I couldn't have written these SQL queries from scratch. But I could guide an agent to do it.

If we can use agents to turn a database into a game engine, what else can we do?

The code is open source. Go break your database.

[Link to Repository]
