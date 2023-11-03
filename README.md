# RandA8
For creating random presets for the Assimil8or

Set a folder full of samples as the path, this script will select up to 380MB of random wav and aiff files from that folder and generate a new output folder. It will also generate a bunch of random sine-based LFOs. If you want, the program will ask if you want to pitch shift the samples. If you choose "Yes", it will detune the samples using an emulation of divide-by-n clock interpolation at random semitones (you can adjust these to your taste). It will then ask if you want the program to generate 100 presets based on these samples. Select "Yes" and you will get a bunch of 4 channel presets (+ LFOs on channel 5). You can adjust the channel distribution/amount to your desires!

For faster loading times on the Assimil8or, use less folder ram (max is 422MB, but it gets slow way before that). 
