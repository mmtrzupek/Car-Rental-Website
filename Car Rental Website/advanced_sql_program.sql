DELIMITER $$
DROP PROCEDURE IF EXISTS TripHistClash $$
CREATE PROCEDURE TripHistClash(IN currUser VARCHAR(255), IN start_dt DATETIME, IN end_dt DATETIME, OUT is_rentable BOOLEAN, OUT is_freeride BOOLEAN)
BEGIN
  DECLARE pk_dt DATETIME;
  DECLARE dr_dt DATETIME;
  
  DECLARE total_rides INT;
  DECLARE freeride BOOL DEFAULT FALSE;
  DECLARE rentable BOOL DEFAULT TRUE;
    
  DECLARE cur CURSOR FOR SELECT pickup_datetime, dropoff_datetime FROM carTripHistory JOIN user ON lesser_id = currUser;
  OPEN cur;
  BEGIN
		DECLARE flag BOOLEAN DEFAULT FALSE;
		DECLARE CONTINUE HANDLER FOR NOT FOUND SET flag = TRUE;
    tLoop: LOOP
			FETCH cur INTO pk_dt, dr_dt;
            
			IF flag THEN LEAVE tLoop;
      END IF;
            
      IF (pk_dt <= start_dt AND dr_dt >= start_dt) OR (pk_dt <= end_dt AND end_dt >= start_dt) THEN
				SET rentable = FALSE, flag = TRUE;
			END IF;
			
		END LOOP tLoop;
        
  END;
  CLOSE cur;


  SELECT COUNT(*) INTO total_rides FROM carTripHistory WHERE lesser_id = currUser;

  IF rentable AND total_rides%20 = 0 THEN SET freeride = TRUE;
  END IF;

  SELECT freeride into is_freeride;
  SELECT rentable INTO is_rentable;
END $$
DELIMITER ;
