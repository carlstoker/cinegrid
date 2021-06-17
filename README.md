# cinegrid
Python script to create mosaics from video files, utilizing ffmpeg and imagemagick. 

#### Usage
```shell
python cinegrid.py [-h] [--bgcolor COLOR] [--border PIXELS] [--b_color COLOR]  
                   [--caps CAPS] [--columns COLUMNS] [--end END]  
                   [--end_percent END] [--h_fontsize PIXELS] [--header]  
                   [--interval INTERVAL] [--max_filesize KB]  
                   [--max_height PIXELS] [--max_width PIXELS] [--output DIR]  
                   [--overwrite] [--prompt] [--shadow] [--spacing SPACING]  
                   [--start START] [--start_percent START]  
                   [--template TEMPLATE] [--t_font FONT] [--t_fontsize PIXELS]  
                   [--timestamp] [--version]  
                   FILE [FILE ...]
```

#### Examples
```shell 
cinegrid -template 3x3 Sintel.2010.720p.mkv
```
![Example image generated using the '3x3' template](../media/Sintel.2010.720p-3x3.jpg?raw=true)

```
cinegrid -template big Sintel.2010.720p.mkv
```
![Example image generated using the 'big' template](../media/Sintel.2010.720p-big.jpg?raw=true)

```
cinegrid -template huge Sintel.2010.720p.mkv
```
![Example image generated using the 'huge' template](../media/Sintel.2010.720p-huge.jpg?raw=true)

```
cinegrid -template mpc Sintel.2010.720p.mkv
```
![Example image generated using the 'mpc' template](../media/Sintel.2010.720p-mpc.jpg?raw=true)

