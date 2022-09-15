# Script by Therefore Games
# yes I should be working on DemonCrawl right now D:
# https://github.com/ThereforeGames/txt2img2img

import os
import string

import modules.scripts as scripts
import gradio as gr
import math

from modules import images
from modules.processing import process_images, Processed
from modules.shared import opts, cmd_opts, state, Options
import modules.sd_samplers
import modules.img2img
import random

def sigmoid(x):
  return 1 / (1 + math.exp(-x))

def choose_string(my_string,delimiter = "|"):
	my_string = my_string.split(delimiter)
	return random.choice(my_string)

class Script(scripts.Script):
	def title(self):
		return "txt2img2img v0.0.1"

	def show(self, is_img2img):
		return not is_img2img

	def ui(self, is_img2img):
		if is_img2img:
			return None
		
		return []

	def run(self, p):

		img2img_term_index = -1

		samplers_dict = {}
		for i, sampler in enumerate(modules.sd_samplers.samplers):
			samplers_dict[sampler.name.lower()] = i

		modules.processing.fix_seed(p)

		img_opts = modules.shared.Options()	

		original_prompt = p.prompt[0] if type(p.prompt) == list else p.prompt
		prompt_parts = original_prompt.split(" ")

		# Create an array of replacement terms based on filenames in the presets directory
		preset_dir = "./txt2img2img"
		preset_files = os.listdir(preset_dir)
		presets = [x.split(".")[0] for x in preset_files]

		print(f"Found the following preset files: {presets}")

		for i, this_part in enumerate(prompt_parts):
			sanitized_part = this_part.translate(str.maketrans('', '', string.punctuation))

			if sanitized_part in presets:
				img2img_term_index = i
				
				# Load settings for this part
				img_opts.load(f"{preset_dir}/{sanitized_part}.json")
				prompt_method = getattr(img_opts,"prompt_method",0)

				# Enable support for randomized prompt paramters
				img_opts.txt2img_term = choose_string(img_opts.txt2img_term)
				img_opts.img2img_term = choose_string(img_opts.img2img_term)

				# Method 0: Replace the placeholder term with user-specified value, leaving the rest of the prompt intact
				if prompt_method == 0:
					prompt_parts[i] = prompt_parts[i].replace(sanitized_part,img_opts.img2img_term)
					img_opts.img2img_prompt = " ".join(prompt_parts)
					prompt_parts[i] = prompt_parts[i].replace(img_opts.img2img_term, img_opts.txt2img_term)
				# Method 1: Replace the placeholder term and delete anything that comes before
				elif prompt_method == 1:
					prompt_parts[i] = prompt_parts[i].replace(sanitized_part,img_opts.img2img_term)
					img_opts.img2img_prompt = " ".join(prompt_parts[i:len(prompt_parts)-1])
				# Method 2: Replace the placeholder term and delete anything that comes after
				elif prompt_method == 2:
					prompt_parts[i] = prompt_parts[i].replace(sanitized_part,img_opts.img2img_term)
					img_opts.img2img_prompt = " ".join(prompt_parts[0:i+1])
					prompt_parts[i] = prompt_parts[i].replace(img_opts.img2img_term, img_opts.txt2img_term)
				# Method 3: Switch the txt2img term with a dummy term and append the img2img term to the end
				elif prompt_method == 3:
					filler_term = choose_string(getattr(img_opts,"filler_term","subject"))
					prompt_parts[i] = prompt_parts[i].replace(sanitized_part,filler_term)
					img_opts.img2img_prompt = " ".join(prompt_parts) + f", {img_opts.img2img_term}"
					prompt_parts[i] = prompt_parts[i].replace(filler_term, img_opts.txt2img_term)
				# Method 4: Replace the entire prompt with the user-specified value
				else:
					img_opts.img2img_prompt = img_opts.img2img_term
					prompt_parts[i] = prompt_parts[i].replace(sanitized_part,img_opts.txt2img_term)


				# TODO: Add support for use of multiple presets within a prompt. For now, let's just kill the loop
				break

		if img2img_term_index > -1:
			# Temporarily disable color correction for this, it tends to make my pics looks washed out
			if (getattr("img_opts","bypass_color_correction",True)):
				temp_color_correction = opts.img2img_color_correction
				opts.img2img_color_correction = False

			denoising_original = getattr(img_opts,"denoising_strength",0.7)
			p.denoising_strength = denoising_original
			p.cfg_scale = getattr(img_opts,"cfg_scale",p.cfg_scale)
			steps_original = getattr(img_opts,"steps",p.steps)
			p.steps = steps_original
			p.prompt = " ".join(prompt_parts)

			# supports batch processing btw
			processed = process_images(p)

			# setup for the magic AI that optimizes your settings
			if getattr(img_opts,"autoconfigure",False):
				from rembg import remove

				max_subject_size = getattr(img_opts,"max_subject_size",0.5)
				min_overfit = 1
				max_overfit = 10
				overfit = min(max_overfit,max(min_overfit,getattr(img_opts,"overfit",5)))

				# TODO: lol hardcoded btw
				min_cfg_scale = 4.0
				min_denoising_strength = 0.36

				total_pixels = p.width * p.height

				# Re-arrange prompt with the goal of improving likeness (edit - this usually does more harm than good)
				# optimal_prompt_position = round(len(prompt_parts) * (overfit / max_overfit))
				# prompt_parts[img2img_term_index] = choose_string(getattr(img_opts,"filler_term","subject"))
				# prompt_parts.insert(optimal_prompt_position, f", {img_opts.img2img_term},")

				#p.prompt = " ".join(prompt_parts)
				#print(f"Prompt optimized as follows: {p.prompt}")
			
			p.prompt = img_opts.img2img_prompt
				

			# Now use our newly created txt2img result(s) with img2img...
			processed_amt = len(processed.images)
			for i in range(processed_amt):
				if (getattr(img_opts,"autoconfigure",False)):
					# Determine best CFG and denoising settings based on size of the subject in the txt2img result				
					transparent_img = remove(processed.images[i])
					# Uncomment the next line to see how the background detection works:
					# transparent_img.save("output.png")

					# Count number of transparent pixels
					transparent_pixels = 0
					img_data = transparent_img.load()
					for y in range(p.height):
						for x in range(p.width):
							pixel_data = img_data[x,y]
							if (pixel_data[3] <= 10): transparent_pixels += 1
					subject_size = 1 - transparent_pixels / total_pixels
					print(f"Detected {transparent_pixels} transparent pixel(s). Your subject is {subject_size*100}% of the canvas.")

					p.steps = steps_original + round(max(0,(subject_size - max_subject_size) / max_subject_size) * (p.steps / 2))
					print(f"Adjusted sampling steps to {p.steps}")

					# Calculate new values using sigmoid distribution, wow so fancy
					p.cfg_scale = max(min_cfg_scale,(p.cfg_scale * 2) * sigmoid(1 - (max_subject_size / subject_size) * (overfit / 5)))
					
					# Lower the denoising strength a bit based on how many more words come after our object
					p.denoising_strength = denoising_original - 0.01 * (len(prompt_parts) - (img2img_term_index + 1)) - 0.02 * " ".join(prompt_parts[0:img2img_term_index+1]).count(')')
					
					# Apply another fancy distribution curve
					p.denoising_strength = max(min_denoising_strength,(p.denoising_strength * 2) * sigmoid(1 - (max_subject_size / subject_size) * (overfit/5)))

					print(f"Updated CFG scale to {p.cfg_scale} and denoising strength to {p.denoising_strength}")


				p.init_images = processed.images[i]
				p.sampler_index = samplers_dict.get(getattr(img_opts,"sampler_name","euler a").lower(), p.sampler_index)
				p.restore_faces = getattr(img_opts,"restore_faces",p.restore_faces)
				p.mask_mode = 0
				p.seed = getattr(img_opts,"seed",p.seed)
				p.negative_prompt = getattr(img_opts,"negative_prompt",p.negative_prompt)

				if p.seed == -1: p.seed = int(random.randrange(4294967294))

				# This feels a bit hacky, but it seems to work for now
				img2img_result = modules.img2img.img2img(
					p.prompt,
					p.negative_prompt,
					p.prompt_style,
					p.init_images,
					None, # p.init_img_with_mask
					None, # p.init_mask
					p.mask_mode,
					p.steps,
					p.sampler_index,
					0, # p.mask_blur
					0, # p.inpainting_fill
					p.restore_faces,
					p.tiling,
					'Redraw whole image', #p.switch_mode
					1,#p.batch_count
					1,#p.batch_size
					p.cfg_scale,
					p.denoising_strength,
					0, # p.denoising_strength_change_factor
					p.seed,
					p.subseed, p.subseed_strength, p.seed_resize_from_h, p.seed_resize_from_w,
					p.height,
					p.width,
					0, # p.resize_mode
					'Irrelevant', # p.sd_upscale_upscaler_name
					0, # p.sd_upscale_overlap
					True, # p.inpaint_full_res
					False, # p.inpainting_mask_invert
					0, # this is the *args tuple and I believe 0 indicates we are not using an extra script in img2img
				)

				# Get the image stored in the first index
				img2img_images = img2img_result[0]

				# Add the new image(s) to our main output
				processed.images.append(img2img_images[0])

			# revert color correction setting
			if (getattr("img_opts","bypass_color_correction",True)):
				opts.img2img_color_correction = temp_color_correction

			return (processed)

		return None