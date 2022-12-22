# Starter Guide

## 1) Download

Visit the main repo page and select **Code > Download Zip**

- https://github.com/ThereforeGames/txt2img2img

Extract the archive into the root directory of Automatic1111's web app. It is advisable to take a backup of the app before performing this installation.

## 2) Setup your routine

Navigate to the `txt2img2img/routines` directory.

This is where your project files live. Each character or subject you want to process through txt2img2img must have its own **routine** JSON file.

In this setup guide, we are going to create a routine for Sheik from The Legend of Zelda:

![Sheik](https://i.ibb.co/gS322Pm/Sheik-Artwork.webp)

We will begin by creating a copy of `example.json` and renaming it to `sheik.json`.

Open up `sheik.json`.

### txt2img_term

We need to replace the value of `txt2img_term` with a short phrase that describes a character who looks like Sheik - someone or something that Stable Diffusion knows how to draw in a variety of contexts. Actors are usually a good choice.

To find our body double, go to https://lexica.art and search for "sheik from the legend of zelda." You can also try alternative phrases like "blonde woman in a ninja outfit."

One of my results contained "Britney Spears" so we'll go with that, she's close enough:

`txt2img_term="Britney Spears wearing a white turban"`

### img2img_term

This must be set to the name of the subject you're trying to create.

In my case, I trained a custom embedding of Sheik using [Textual Inversion](https://github.com/nicolai256/Stable-textual-inversion_win). If you don't know what that is, go read up - it's outside the scope of this tutorial. The gist is that you can teach Stable Diffusion about characters that are not well represented in the base model. Problem is, those new characters often don't respond well to prompts. It will draw your character, but if you ask for "my character in a space setting with blue eyes and green shoes" it will probably ignore everything except "my character." The purpose of txt2img2img is a way of getting around that.

My custom embedding of sheik is called sheik_v1.pt so I set the value accordingly:

`img2img_term="sheik_v1"`

## 3) Run the script

You can leave all the other JSON options at their default values.

Save the file and boot up your web UI.

For your prompt, enter a phrase that contains the filename of your JSON file - this is how txt2img2img knows what to process.

Example prompt:

`An illustration of sheik in a cherry blossom forest.`

Scroll to the bottom of the UI and select `txt2img2img vX.X.X` from the Script dropdown menu.

Press Generate.

If you set up everything correctly, you will receive two images:

![Results](https://i.ibb.co/Krf42zt/brave-u-K1-Hl-N3-S21.png)

If your results are poor, it is time to return to the main repo page and read up on the **JSON Options** section:

- https://github.com/ThereforeGames/txt2img2img#json-options

For further assistance, please consider joining us on the [Stable Diffusion Discord](https://discord.gg/stablediffusion) or [opening up an issue here](https://github.com/ThereforeGames/txt2img2img/issues). Good luck!
