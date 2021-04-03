import { Rating } from "./rating.js";
import { Star } from "./star.js";
import { Tags } from "./tags.js";

export function SongTable(props) {
    return (
      <table className={`song-table table table-striped table-condensed table-hover ${props.extraClasses}`}>
        {props.showHeader && <thead>
          <tr>
            <th>&nbsp;</th>
            <th>Name</th>
            <th>Artist</th>
            <th>Albums</th>
            <th>Year</th>
            <th>Rating</th>
            <th>Energy</th>
            <th>Mood</th>
            <th>Tags</th>
          </tr>
        </thead>}
        <tbody>
          {props.songs.map((song) => (
            <tr key={song.id}>
              <td className="icon-cell is-starred">
                  <Star id={song.id} value={song.starred} />
              </td>
              {song.track_number && <td>{song.track_number}.</td>}
              <td className="col-sm-2">{song.name}</td>
              <td>{song.artist}</td>
              <td>{song.albums}</td>
              <td>{song.year}</td>
              <Rating id={song.id} field="rating" icon="star" value={song.rating} />
              <Rating id={song.id} field="energy" icon="fire" value={song.energy} />
              <Rating id={song.id} field="mood" icon="heart" value={song.mood} />
              <Tags id={song.id} value={song.tags.join(" ")} />
            </tr>
          ))}
        </tbody>
      </table>
    );
}