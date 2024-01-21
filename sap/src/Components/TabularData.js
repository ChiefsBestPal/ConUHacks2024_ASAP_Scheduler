import React, { useState, useEffect } from 'react';
import './TabularData.css';
import { addDays, format } from 'date-fns';

const timelineHours = Array.from({ length: 12 }, (_, i) => `${7 + i}:00`);






let bays = [
    {
        bay: "Bay 1",
        reservations: [
            { start: "7:00", end: "8:30", type: "a" },
            { start: "9:00", end: "10:30", type: "a" },
            { start: "10:30", end: "11:30", type: "a" },
            { start: "13:30", end: "14:30", type: "a" },
        ],
    },
    {
        bay: "Bay 2",
        reservations: [
            { start: "7:30", end: "9:00", type: "a" },
            { start: "9:00", end: "10:30", type: "a" }
        ],
    },
    {
      bay: "Bay 3",
      reservations: [
          { start: "7:00", end: "8:30", type: "a" },
          { start: "9:00", end: "10:30", type: "a" },
          { start: "10:30", end: "11:30", type: "a" },
          { start: "13:30", end: "14:30", type: "a" },
      ],
    },
    {
      bay: "Bay 4",
      reservations: [
          { start: "7:00", end: "8:30", type: "a" },
          { start: "9:00", end: "10:30", type: "a" },
          { start: "10:30", end: "11:30", type: "a" },
          { start: "13:30", end: "14:30", type: "a" },
      ],
    },
    {
      bay: "Bay 5",
      reservations: [
          { start: "7:00", end: "8:30", type: "a" },
          { start: "9:00", end: "10:30", type: "a" },
          { start: "10:30", end: "11:30", type: "a" },
          { start: "13:30", end: "14:30", type: "a" },
      ],
    },
    {
      bay: "Bay 6",
      reservations: [
          { start: "7:00", end: "8:30", type: "a" },
          { start: "9:00", end: "10:30", type: "a" },
          { start: "10:30", end: "11:30", type: "a" },
          { start: "13:30", end: "14:30", type: "a" },
      ],
    },
    {
      bay: "Bay 7",
      reservations: [
          { start: "7:00", end: "8:30", type: "a" },
          { start: "9:00", end: "10:30", type: "a" },
          { start: "10:30", end: "11:30", type: "a" },
          { start: "13:30", end: "14:30", type: "a" },
      ],
    },
    {
      bay: "Bay 8",
      reservations: [
          { start: "7:00", end: "8:30", type: "a" },
          { start: "9:00", end: "10:30", type: "a" },
          { start: "10:30", end: "11:30", type: "a" },
          { start: "13:30", end: "14:30", type: "a" },
      ],
    },
    {
      bay: "Bay 9",
      reservations: [
          { start: "7:00", end: "8:30", type: "a" },
          { start: "9:00", end: "10:30", type: "a" },
          { start: "10:30", end: "11:30", type: "a" },
          { start: "13:30", end: "14:30", type: "a" },
      ],
    },
    {
      bay: "Bay 10",
      reservations: [
          { start: "7:00", end: "8:30", type: "a" },
          { start: "9:00", end: "10:30", type: "a" },
          { start: "10:30", end: "11:30", type: "a" },
          { start: "13:30", end: "14:30", type: "a" },
      ],
    },
];

function getAllData() {
  fetch('http://localhost:5000/api/get_bays_interval_list', {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json'
    },
    //body: JSON.stringify({ key: 'value' }) // Replace with your data object
  }).then(
    response => response.json()
  ).then(
    data => {
      bays = data;
    }
  )
}


function calculateReservationPositionAndWidth(reservation, totalHours) {
  const timeToFraction = time => {
      const [hours, minutes] = time.split(':').map(Number);
      return hours + minutes / 60;
  };

  const startFraction = timeToFraction(reservation.start);
  const endFraction = timeToFraction(reservation.end);

  const startPosition = (((startFraction - 7) / totalHours) * 100);
  const endPosition = (((endFraction - 7) / totalHours) * 100);
  const width = endPosition - startPosition;

  return { startPosition, width };
}

export default function TabularData() {
  const [width, setWidth] = useState(window.innerWidth);

  useEffect(() => {
      const handleResize = () => {
          setWidth(window.innerWidth);
      };

      window.addEventListener('resize', handleResize);
      return () => window.removeEventListener('resize', handleResize);
  }, []);



  const [currentDate, setCurrentDate] = useState(new Date('2022-10-02'));

  useEffect(() => {
      const handleResize = () => {
          setWidth(window.innerWidth);
      };

      window.addEventListener('resize', handleResize);
      return () => window.removeEventListener('resize', handleResize);
  }, []);

    const goToPreviousDay = () => {
        setCurrentDate(prevDate => addDays(prevDate, -1));
    };

    const goToNextDay = () => {
        setCurrentDate(prevDate => addDays(prevDate, 1));
    };

    const formattedDate = format(currentDate, 'yyyy-MM-dd');

    useEffect(() => {
      getAllData(); // Call the function when the component mounts and when currentDate changes
    }, [currentDate]);

  return (
    <div className='tabularContainer'>
      <div className='dateNavigation'>
          <button className='b1' onClick={goToPreviousDay}>&lt;</button>
          <span>{formattedDate}</span>
          <button className='b2' onClick={goToNextDay}>&gt;</button>
      </div>
      <div className='tableContainer'>
          <table className='tabularData'>
              <thead>
                  <tr>
                      <th>Bays/Times</th>
                      {timelineHours.map(hour => (
                          <th key={hour} style={{ width: `${100/timelineHours.length}%` }}>{hour}</th>
                      ))}
                  </tr>
              </thead>
              <tbody>
                {bays.map(bay => (
                    <tr key={bay.bay}>
                        <td>{bay.bay}</td>
                        <td colSpan={timelineHours.length}>
                            <div style={{ position: 'relative', width: '100%', height: '30px' }}>
                                {bay.reservations.map((reservation, index) => {
                                    const { startPosition, width } = calculateReservationPositionAndWidth(reservation, timelineHours.length);
                                    const isEven = index % 2 === 0;

                                    const reservationStyle = {
                                        position: 'absolute',
                                        left: `calc(${startPosition}%)`,
                                        width: `calc(${width}%)`,
                                        height: '30px',
                                        up: '12px',
                                        backgroundColor: isEven ? '#363062' : '#687EFF',
                                        border: `1px solid white`
                                    };

                                    return (
                                        <div key={index} style={reservationStyle}>
                                            {reservation.type}
                                        </div>
                                    );
                                })}
                            </div>
                        </td>
                    </tr>
                ))}
</tbody>


          </table>
      </div>
      </div>
      

  );
}
