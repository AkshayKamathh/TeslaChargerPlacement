import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import { useState } from 'react';
import axios from 'axios';

export default function MapComponent({ parkingLots }) {
    const [ownership, setOwnership] = useState({});

    const fetchOwnership = async (lat, lon) => {
        const res = await axios.get(`http://127.0.0.1:5000/get-ownership?lat=${lat}&lon=${lon}`);
        setOwnership({ [`${lat},${lon}`]: res.data });
    };

    return (
        <MapContainer center={[39.8283, -98.5795]} zoom={5} style={{ height: '500px', width: '100%' }}>
            <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
            {parkingLots.map((lot, idx) => (
                <Marker key={idx} position={[lot.lat, lot.lon]}>
                    <Popup>
                        <b>{lot.name}</b><br />
                        <button onClick={() => fetchOwnership(lot.lat, lot.lon)}>Who Owns This?</button>
                        {ownership[`${lot.lat},${lot.lon}`] && (
                            <p><b>Owner:</b> {ownership[`${lot.lat},${lot.lon}`].owner || 'Unknown'}</p>
                        )}
                    </Popup>
                </Marker>
            ))}
        </MapContainer>
    );
}
