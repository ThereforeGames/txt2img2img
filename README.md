# txt2img2img for Stable Diffusion
Greatly improve the editability of any character/subject while retaining their likeness.

## Introduction
txt2img2img is an experimental addon for [AUTOMATIC1111's Stable Diffusion Web UI](https://github.com/AUTOMATIC1111/stable-diffusion-webui) that streamlines the process of running a prompt through txt2img, then running its output through img2img using pre-defined parameters.

In addition to the ability to define your own keywords and presets, txt2img2img can intelligently auto-adjust the parameters for the img2img phase based on what the the txt2img output looks like.

We can approximate the "best" settings for img2img (denoise, CFG scale, inference steps) by considering how big or small the subject is within an image. This saves you the time and hassle of having to flip through pages in the UI and fiddle with sliders manually.

This is a work in progress - more docs and features will be added over time.

## Purpose

The main motivation for this script is improving the editability of embeddings created through [Textual Inversion](https://textual-inversion.github.io/).

There is an ongoing question in the Stable Diffusion community to figure out how we can finetune new subjects such that they respond well to complex prompts. Textual Inversion is great at high fidelity reproduction, but it is notoriously quick to "overfit."

Here's what I've observed: when people say an embedding has been "overfitted," they are usually talking about txt2img. As it turns out, our embeddings are still quite flexible in img2img mode - as long as you provide sensible initial images, you can morph the model into contexts that would be outright impossible with txt2img.

Here's how txt2img2img can help:

- You start by creating a config file for a subject with weak editability
- In that file, you define a "body double" - this is a prompt fragment with a name or phrase of someone or something that closely resembles your subject
- Whenever your subject's name is detected in a prompt, it is quietly replaced with the body double and processed with txt2img
- The txt2img result then goes through img2img using your original prompt, and voila, your subject is effectively "de-overfitted"

You can, of course, use this script without finetuned embeddings. You can think of it as a general purpose "prompt swapper" if you like. Play around with it and see if you find any other cool use cases.

## Does it work?

In my experience, yes!

Here's an example that shows the difference with the script on/off - this demonstrates a checkpoint of Sheik images from The Legend of Zelda. It was trained for 50k+ iterations and has lost basically all understanding of the English language. While it can produce a good Sheik, it ignores just about anything else I put into the prompt.

txt2img2img takes care of the issue nicely:

![txt2img2img_example](https://user-images.githubusercontent.com/95403634/190363773-f0d94355-cb18-4f7c-ae99-c205858fc085.png)

More examples to come.

## Installation

Simply clone or download this repo and place the files in the base directory of Automatic's web UI.

***Note:** this repo includes several Python modules for [Rembg](https://github.com/danielgatis/rembg) and its requirements. Rembg is needed for background detection as part of txt2img2img's "autotuning" feature. You are welcome to install these packages manually if you prefer, but I had a hard time getting Rembg to cooperate with Automatic's install script. Alternatively, you can skip these files as long as you set `autoconfigure` to false in your preset configs.*

## Usage

From the txt2img screen, select txt2img2img as your active script:

![image](https://user-images.githubusercontent.com/95403634/190369520-41ca3584-87fd-42cc-8439-588b3a998a23.png)

Now, you will need to set up preset(s) for your subjects. Each preset is created as a JSON file inside the `/txt2img2img` directory of the web app.

Check the included files of that directory to get a better understanding of how they work - it is mostly self-explanatory, but please see the next section for detailed instructions.

The filenames of your presets (minus '.json') are used as "keywords" in your prompt for txt2img2img processing.

## JSON Options

#### General notes:
- You can modify your JSON options without having to restart the web app. Any changes will take effect the next time you generate an image.

#### txt2img_term (str)
- This is a "body double" that has strong editability for your subject. If you're making human characters, try entering an actor's name here. SD has a very good grasp on most people in Hollywood. Alternatively, you can try a short, generic phrase to approximate the look of your subject (e.g. "a blonde woman wearing a white turban") but in my experience this leads to less consistent results. 
- Try looking up your subject on [https://lexica.art/](lexica.art) for possibilities.
- Supports randomization with the `|` delimiter, e.g. `Batman|Superman|Danny DeVito` will cause the script to pick from one of those three at random, every generation.

#### img2img_term (str)
- This is direct prompt fragment for your subject, e.g. the filename of your finetuned embedding.
- Supports randomization with the `|` delimter.

#### autoconfigure (bool)
- Determines whether the script should intelligently adjust values for img2img processing. See next section for more info.

#### negative_prompt (str)
- Informs the script about what to avoid during img2img processing. Very powerful - play around with it to figure out the difference between negating terms during txt2img versus img2img.

#### sampler_name (str)
- Specify a sampler to use with img2img.
- If unspecified, it will use the sampler you have selected on the txt2img page.

#### seed (int)
- The seed for inference with img2img.
- If unspecified, it will use the same seed as you have selected on the txt2img page. This is probably ideal.
- You can set it to -1 for random seed.

#### steps (int)
- The number of inference steps for img2img processing.
- If unspecified, it will use the same number of steps as shown on the txt2img page.

#### cfg_scale (float)
- The classifier free guidance scale for inference with img2img.
- If unspecified, it will use the same value as shown on the txt2img page.

#### denoising_strength (float)
- Defaults to 0.7.
- The "best" value here largely depends on the amount of visual difference between your body double and subject. If the two look very much alike, you don't need to set denoise very high.

#### restore_faces (bool)
- Whether to restore faces after img2img processing.
- If unspecified, it will use the same value as shown on the txt2img page.

#### bypass_color_correction (bool)
- If enabled, the script will ignore the global color correction setting of the web app.
- In my experience, the color correction can lead to pictures that look a bit washed out. I'm not sure if this is an issue with the color correction, or just the way it interacts with my finetuned objects.

#### prompt_method (int 0-4)
- This determines how your prompt is sliced up for img2img processing. When in doubt, leave it at 0.
- **0:** The keyword (i.e. the JSON filename) will be replaced with your `img2txt_term` value. No further processing. This is generally the best option.
- **1:** Delete any words in the prompt that come before the keyword.
- **2:** Delete any words in the prompt that come after the keyword.
- **3:** Replace the keyword with a generic dummy term (defined by `filler_term` in the JSON) and append your `img2txt_term` value to the end of the prompt.
- **4:** Replace the entire prompt with `img2txt_term`.

#### overfit (int 1-10)
- Defaults to 5.
- This value determines the aggression of the autotuner. A higher value means the autotuner will work harder to counteract the inflexibility of a subject.
- Work in progress, wouldn't suggest messing with it right now.

#### max_subject_size (float 0 to 1)
- Defaults to 0.5.
- This value indicates the density of a subject's presence within the txt2img result before the autotuner caps out on certain adjustments.
- 0.5 means the subject occupies 50% of the image's pixels.

#### daisychain (bool)
- If enabled, the preset will pass its image (either txt2img or img2img generation) to a different preset file and perform another img2img operation using the settings of the new file.
- The next preset is specified as the value of `txt2img_term`. Set it to a filename without an extension.
- What this means is that you can create a custom "chain" of automated txt2img2img2img2img...2img operations. Why would you want to do this? Well, you might want to add a specific object to your body double that is hard to achieve in one pass. Maybe you want to give your body double a particular kind of hat - a standalone img2img operation for this may yield better results.
- Be careful, you can create an infinite loop if you daisychain back and forth between the same files. There are no safety checks in place yet. Use your new superpowers responsibly.

## The Autotuner

One of the unique features in txt2img2img is its ability to automatically adjust SD settings before the img2img step. It does this in a variety of ways:

- It scans the txt2image result to determine how many pixels are occupied by the subject vs the background. The size of your subject influences the CFG scale, denoise strength, and even step count (mildly.)
- It uses the values in your JSON file as "starting points" for its adjustments
- It will further adjust the denoising strength based on how many words and parentheses appear in the prompt after the keyword. More words = more concepts = a need for slightly lower denoise strength.
- You can make it autotune harder by increasing the `overfit` value in your JSON file.

## Known Issues

- If the script crashes due to "img2img_color_correction" it likely means your web UI is not up to date. The color correction feature was added very recently.
- If the script crashes due to a missing "u2net.onnx" file, you can download the file in question using the Google Drive link provided in the error screen. This file is a dependency of the Rembg module. You can also work around the issue by disabling `autoconfig` in your JSON file.

## Tips & Final Thots

- If your subject likeness is poor, I highly recommend looking into "prompt weighting." Automatic's UI has a form of weighting with parentheses, but in my experience it doesn't help much with overtrained models - check [this post](https://github.com/AUTOMATIC1111/stable-diffusion-webui/issues/70#issuecomment-1237380147) for another implementation that makes a world of difference. It does require splicing in a few blocks of code into `scripts/processing.py`. Afterwards, you can set your `img2img_term` to something like "mycharacter:10" - the higher the value, the better the likeness (at a little cost to editability.) This feature is practically mandatory for my finetuned models.
- Currently, the web UI's progress bar doesn't account for the img2img step. It'll say 100% at the halfway mark.
- Batch processing should work fine.
- img2img metadata is not available in the UI, but some info is printed to the console and all images should save to disk as usual.
- Calling img2img from the txt2img page is a little hack-y and could break between updates of the UI app. I'm looking for a way of futureproofing it.

Feel free to [open an issue](https://github.com/ThereforeGames/txt2img2img/issues) if you have any questions or run into problems.

Enjoy!
