import React, { useState } from "react";
import Popover from "@mui/material/Popover";
import Typography from "@mui/material/Typography";
import Button from "@mui/material/Button";
import LibLabel from "./libLabel";

export default function BasicPopover({ name, checkedInputs, setCheckedInputs }) {
  const [anchorEl, setAnchorEl] = useState(null);
  const handleClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const open = Boolean(anchorEl);
  const id = open ? "simple-popover" : undefined;

  return (
    <div>
      <Button
        aria-describedby={id}
        variant="contained"
        onClick={handleClick}
        className="ms-auto libBox-mini-dodo"
        sx={{
          backgroundColor: "transparent",
          color: "#4F4E4E",
          fontFamily: "NEXON",
          p: 0,
          fontSize: window.innerWidth > 1441 ? "25px" : "16px",
        }}>
        {name}
      </Button>
      <Popover
        id={id}
        open={open}
        anchorEl={anchorEl}
        onClose={handleClose}
        anchorOrigin={{
          vertical: "bottom",
          horizontal: "left",
        }}>
        <Typography
          sx={{
            p: 0,
            width: window.innerWidth > 1441 ? "400px" : "300px",
            height: "100%",
            "& .MuiPopover-paper": { backgroundColor: "transparent" },
          }}>
          <LibLabel checkedInputs={checkedInputs} setCheckedInputs={setCheckedInputs} />
        </Typography>
      </Popover>
    </div>
  );
}
