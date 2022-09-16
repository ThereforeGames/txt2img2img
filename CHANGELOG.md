# Changelog
All notable changes to this project will be documented in this file.

## 1.0.0 - 16 September 2022
### Added
- Changelog, let's start treating this like proper software
- New prompt templating system that replaces the hardcoded 'prompt_methods'
- If the 'prompt_template' value in your routine does not resolve to a file that exists, its value will be used as a hardcoded template instead
- Experimental 'prompt2prompt_inversion' template that takes advantage of the new prompt weighting feature in the UI - it may have superior details when compared to the default template, but likeness suffers a bit, gonna keep working on it
- Shortcode support for prompt templates, see docs for more info

### Changed
- "Presets" are now known as "Routines" and are loaded from "./txt2img2img/routines" directory
- The 'prompt_method' setting is now 'prompt_template' and should point to a txt file in the "./txt2img2img/prompt_templates" directory
- Prompt complexity is now determined by the number of tokens as opposed to string length
- example.json is hopefully a little more clear

## 0.0.2 - 15 September 2022
### Added
- Daisychaining feature that allows you to bounce between files and create a custom "chain" of img2img operations

### Changed
- Basic safety checks
- Various bug fixes

## 0.0.1 - 15 September 2022
- Initial release