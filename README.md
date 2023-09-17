# dj-orange

My Django playground, with two main apps.

## Rhyme

Rhyme is a web app to manage a user's music collection and generate highly individualized playlists, combining standard metadata with a user's individual ratings and tagging.

Rhyme replaces [an earlier, Perl-based web app](https://github.com/orangejenny/flavors).

### Songs

Rhyme stores basic metadata; user-specific ratings for quality, mood, and energy; and user-specific tags.
Tags can be grouped into categories that enable higher-level querying and certain visualizations.

Songs can be filtered by simple attributes or by complex query.

Any filtered set of songs can then be exported into a playlist, an M3U file based on local filenames. Different devices with different file hierarchies can be configured.

![screenshot of song list](https://github.com/orangejenny/dj-orange/blob/master/readme/songs.png?raw=true)

### Albums

Albums store some additional metadata. Playlsits can be generated based on albums instead of songs.

![screenshot of album list](https://github.com/orangejenny/dj-orange/blob/master/readme/albums.png?raw=true)

### Visualizations

Visualizations allow exploration of data and the generation of novel playlists.

#### Network: interactive exploration of tags that appear together

![screenshot of network visualization](https://github.com/orangejenny/dj-orange/blob/master/readme/network.png?raw=true)

#### Matrix: combining mood and energy

![screenshot of matrix visualization](https://github.com/orangejenny/dj-orange/blob/master/readme/matrix.png?raw=true)

### Additional Commands

Additional commands support:

* Integration with [plex media server](https://www.plex.tv)
* Quick console-based data entry
* Additional complex querying and playlist generation

## Kilo

Kilo tracks workouts. It's pretty basic. The front end is React.

Kilo replaces [a previous workouts app](https://github.com/orangejenny/miles/) based on D3 and [an even older one](https://github.com/orangejenny/workouts/) from way back when I was into Rails.

* Create and update workouts
* View personal records
* View graphs of workout frequency and pace, which demonstrate that I'm consistent about working out and also that I only have one running pace, regardless of whether I'm going four miles or ten. I do speed up a tiny bit for track intervals and slow down a little for marathons.

![screenshot of frequency page](https://github.com/orangejenny/dj-orange/blob/master/readme/frequency.png?raw=true)

![screenshot of recent workouts page](https://github.com/orangejenny/dj-orange/blob/master/readme/recent.png?raw=true)

![screenshot of pace page](https://github.com/orangejenny/dj-orange/blob/master/readme/pace.png?raw=true)
