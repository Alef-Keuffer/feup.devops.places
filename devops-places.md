`Lab work. Event management. (conferences, festivals, trade shows, concerts, corporate meetings).`

`Event: target number of participants. Specify day or interval of dates.`

`Promoters/users.`

`Places. Number of rooms. Size (number of persons, square meters). Cost. Availability.`

`Tickets. Payments.`

`Reviews. (Event, Place).`

`We are group 5. We chose "Places".`

# **`General requirements for the system`**

# **`The problem from "places" perspective`**

`A promoter will plan an event. It needs to take into account where it can happen depending on its needs. We might want to plan the event based on different aspects of the venues (i.e. places) available:`

* `number of rooms`  
* `size. Can be expressed as square meters.`  
* `layout. Can be expressed through an image.`  
* `images of the venue.`  
* `cost. Promoters have budgets and need to take into account the cost of renting the venue. This cost might be expressed as cost/day, cost/date.`  
* `availability`  
  * `depends if there are other events scheduled for the desired date`  
* `reputation`  
  * `depends on reviews. The promoter might want the event to only occur at venues that are above a certain rating.`  
* `a concrete location (maybe a latitude/longitutde pair)`  
* `Equipment (# chairs, projectors, tables, Tvs, lights, Etc)`


**`Requirements:`**

| `Functional Requirements` | `Non Functional Requirements` |
| :---- | :---- |
| `The system shall allow users to retrieve the place price` | `The Places Service shall restrict modifications to place information only to authorized users.` |
| `The system shall allow users to validate the availability of a place for a specified date and time` | `The Places Service shall exchange information with other microservices using standardized API`  |
| `The system shall allow users to find available rooms/places for the capacity requested` | `The Places Service shall ensure that confirmed changes to place availability are reflected in subsequent availability queries.`  |
|  | `The Places Service shall respond to 95% of availability queries within 2 seconds under normal operating conditions.`  |
|  |  |

**`System Operation:`**

**`We need to define whether place service is allowed to write and read. Just read and another service/entitity writes.`**

**`Is the Places Service responsible only for retrieving place information, or should it also support creating, updating, and deleting places?`** 

**`Is Places responsible for managing individual rooms within a venue, or does each place represent an entire venue?`** 