from fastapi import APIRouter, HTTPException, Query

from ..settings import STUDENT_EMAIL

router = APIRouter()


@router.get("/stats")
async def stats(values: str = Query(...)):
    nums = []
    for part in values.split(","):
        part = part.strip()
        if not part:
            continue
        try:
            nums.append(int(part))
        except ValueError:
            try:
                nums.append(float(part))
            except ValueError:
                raise HTTPException(422, f"bad value: {part!r}")
    if not nums:
        raise HTTPException(422, "no values")
    s = sum(nums)
    return {"email": STUDENT_EMAIL, "count": len(nums), "sum": s,
            "min": min(nums), "max": max(nums), "mean": s / len(nums)}
