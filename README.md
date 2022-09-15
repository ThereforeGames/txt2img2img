# txt2img2img for Stable Diffusion
Greatly improve the editability of any character/subject while retaining their likeness.
## Introduction
txt2img2img is an experimental addon for [AUTOMATIC1111's Stable Diffusion Web UI](https://github.com/AUTOMATIC1111/stable-diffusion-webui) that streamlines the process of running a prompt through txt2img, then running its output through img2img using pre-defined parameters.

In addition to the ability to define your own keywords and presets, txt2img2img can intelligently auto-adjust the parameters for the img2img phase based on what the the txt2img output looks like.

We can approximate the "best" settings for img2img (denoise, CFG scale, inference steps) by considering how big or small the subject is within an image. This saves you the time and hassle of having to flip through pages in the UI and fiddle with sliders manually.

This is a work in progress - more docs and features will be added over time.

## Purpose

The main motivation for this script is improving the editability of embeddings created through [Textual Inversion](https://textual-inversion.github.io/).

There is something of an ongoing question in the Stable Diffusion community to figure out how we can finetune new subjects such that they respond well to complex prompts. Textual Inversion is great at high fidelity reproduction, but it is notoriously quick to "overfit."

Here's the interesting thing: when people say an embedding has been "overfitted," they are usually talking about txt2img. As it turns out, our embeddings are still quite flexible in img2img mode - as long as you provide sensible initial images, you can morph your model into contexts that would be outright impossible with txt2img.

Here's how txt2img2img helps:

- You start by creating a config file for a subject with weak editability
- In that file, you define a "body double" - this is a prompt fragment with a name or phrase of someone or something that closely resembles your subject
- Whenever your subject's name is detected in a prompt, it is quietly replaced with the body double for txt2img processing
- The txt2img result is then processed with img2img using your original prompt, and voila, your subject is effectively "un-overfitted"

## Does it work?

In my experience, yes! Here's an example that shows the difference with the script on/off - this demonstrates a checkpoint of Sheik images from The Legend of Zelda. It was trained for 50k+ iterations and has lost basically all understanding of the English language. It can produce a good Sheik, but ignores just about anything else I put into the prompt.

